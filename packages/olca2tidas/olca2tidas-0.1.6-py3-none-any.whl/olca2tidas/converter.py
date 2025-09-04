

import argparse
import json
import os
import re
import shutil
import sys
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def _uuid():
    return str(uuid.uuid4())

def _is_uuid_like(s: str) -> bool:
    try:
        uuid.UUID(str(s))
        return True
    except Exception:
        return False

def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _dump_json(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def _text_lang(zh: str = None, en: str = None):
    arr = []
    if zh:
        arr.append({"#text": zh, "@xml:lang": "zh"})
    if en:
        arr.append({"#text": en, "@xml:lang": "en"})
    return arr or [{"#text": "", "@xml:lang": "en"}]

def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def regroup_folders(src_root: Path, out_root: Path):
    """
    将 src_root 的内容复制/整理到 out_root：
      - data 下包含：flow_properties, flows, lifecyclemodels(由 product_systems 重命名), processes, sources, unit_groups
      - 其他放到 other 下
    """
    data_dir = out_root / "data"
    other_dir = out_root / "other"
    data_dir.mkdir(parents=True, exist_ok=True)
    other_dir.mkdir(parents=True, exist_ok=True)

    product_systems_name = "product_systems"
    lifecyclemodels_name = "lifecyclemodels"

    data_folders = {"flow_properties", "flows", lifecyclemodels_name,
                    "processes", "sources", "unit_groups"}

    for item in os.listdir(src_root):
        src_path = src_root / item
        mapped_name = lifecyclemodels_name if item == product_systems_name else item

        dst_base = data_dir if mapped_name in data_folders else other_dir
        dst_path = dst_base / mapped_name

        if src_path.is_dir():
            shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
        else:
            shutil.copy2(src_path, dst_path)

    print(f"[1/5] 目录重组完成：{out_root}")



ILCD_MASS_UUID = "93a60a56-a3c8-11da-a746-0800200b9a66"

ZH_NAME_MAP = {
    "Benzene": "苯",
    "Carbon dioxide": "二氧化碳",
    "Methane": "甲烷",
    "Ammonia": "氨",
}

def _slug(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_").replace(">", "_").replace("\\", "_").replace("/", "_")

def _classes_from_category(cat: str):
    """把 'A/B/C' 或 'A>B>C' 等切分为 common:class[level=i]"""
    if not cat:
        return [{
            "@level": "0",
            "@classId": "elementary_flows",
            "#text": "Elementary flows"
        }]
    for delim in ["/", ">", "\\"]:
        if delim in cat:
            parts = [p.strip() for p in cat.split(delim) if p.strip()]
            break
    else:
        parts = [cat.strip()] if cat.strip() else []
    classes = []
    acc = []
    for i, p in enumerate(parts):
        acc.append(p)
        classes.append({
            "@level": str(i),
            "@classId": _slug("/".join(acc)),
            "#text": p
        })
    return classes or [{
        "@level": "0",
        "@classId": "uncategorized",
        "#text": "Uncategorized"
    }]

def _pick_mass_property_uuid(flow_properties) -> str:
    """尽量沿用源数据的参考 flowProperty UUID，否则回退为 ILCD 质量 UUID。"""
    if isinstance(flow_properties, list):
        for fp in flow_properties:
            try:
                if fp.get("isRefFlowProperty") and fp.get("flowProperty", {}).get("@id"):
                    return fp["flowProperty"]["@id"]
            except Exception:
                continue
    return ILCD_MASS_UUID

def _detect_type_of_dataset(flow_type_src: str, override: str = None) -> str:
    if override:
        return override
    ft = (flow_type_src or "").strip().upper()
    if "ELEMENTARY" in ft:
        return "Elementary flow"
    if "WASTE" in ft:
        return "Waste flow"
    if "PRODUCT" in ft:
        return "Product flow"
    return "Product flow"

def _default_name_fields(type_of_ds: str, category_path: str):
    classes = _classes_from_category(category_path)
    tail = " / ".join([c["#text"] for c in classes[-2:]]) if len(classes) >= 2 else (classes[-1]["#text"] if classes else "")
    if type_of_ds == "Elementary flow":
        tsr_en = f"{tail} - elementary flow" if tail else "Elementary flow"
        tsr_zh = f"{tail} — 基元流" if tail else "基元流"
        mix_en, mix_zh = "Elementary flow", "基元流"
    elif type_of_ds == "Waste flow":
        tsr_en = "Waste flow - treatment route not specified"
        tsr_zh = "废物流 — 处理路线未指定"
        mix_en, mix_zh = "Waste flow", "废物流"
    else:
        tsr_en = "Processing / production technology not specified"
        tsr_zh = "加工 / 生产工艺未指定"
        mix_en, mix_zh = "Production mix, in the factory", "生产混合，在工厂"
    flowprop_en, flowprop_zh = "kg", "千克"
    return (
        [{"#text": tsr_zh, "@xml:lang": "zh"}, {"#text": tsr_en, "@xml:lang": "en"}],
        [{"#text": mix_zh, "@xml:lang": "zh"}, {"#text": mix_en, "@xml:lang": "en"}],
        [{"#text": flowprop_zh, "@xml:lang": "zh"}, {"#text": flowprop_en, "@xml:lang": "en"}],
    )

def convert_flow_one(src_dict: dict,
                     name_zh_override: str = None,
                     synonyms_en: list = None,
                     synonyms_zh: list = None,
                     flow_type_override: str = None,
                     category_override: str = None) -> list:
    """单个 Flow JSON → ILCD Flow（顶层为数组，内含一个对象）。"""
    flow_id = src_dict.get("@id") or _uuid()
    name_en = src_dict.get("name") or "Unnamed flow"
    name_zh = name_zh_override or ZH_NAME_MAP.get(name_en, name_en)

    category_path = category_override or src_dict.get("category", "")
    classes = _classes_from_category(category_path)

    mass_prop_uuid = _pick_mass_property_uuid(src_dict.get("flowProperties"))
    type_of_ds = _detect_type_of_dataset(src_dict.get("flowType"), flow_type_override)

    treatmentStandardsRoutes, mixAndLocationTypes, flowProps_text = _default_name_fields(type_of_ds, category_path)

    syn_en = [{"#text": s.strip(), "@xml:lang": "en"} for s in (synonyms_en or []) if s.strip()]
    syn_zh = [{"#text": s.strip(), "@xml:lang": "zh"} for s in (synonyms_zh or []) if s.strip()]
    synonyms = syn_en + syn_zh if (syn_en or syn_zh) else [
        {"#text": f"{name_en}", "@xml:lang": "en"},
        {"#text": f"{name_zh}", "@xml:lang": "zh"},
    ]

    ilcd = [
        {
            "flowDataSet": {
                "@xmlns": "http://lca.jrc.it/ILCD/Flow",
                "@xmlns:common": "http://lca.jrc.it/ILCD/Common",
                "@xmlns:ecn": "http://eplca.jrc.ec.europa.eu/ILCD/Extensions/2018/ECNumber",
                "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "@version": "1.1",
                "@locations": "../ILCDLocations.xml",
                "@xsi:schemaLocation": "http://lca.jrc.it/ILCD/Flow ../../schemas/ILCD_FlowDataSet.xsd",
                "flowInformation": {
                    "dataSetInformation": {
                        "common:UUID": flow_id,
                        "name": {
                            "baseName": [
                                {"#text": name_en, "@xml:lang": "en"},
                                {"#text": name_zh, "@xml:lang": "zh"}
                            ],
                            "treatmentStandardsRoutes": treatmentStandardsRoutes,
                            "mixAndLocationTypes": mixAndLocationTypes,
                            "flowProperties": flowProps_text
                        },
                        "common:synonyms": synonyms,
                        "classificationInformation": {
                            "common:classification": {
                                "common:class": classes
                            }
                        },
                        "common:generalComment": [
                            {"#text": src_dict.get("description", "").strip() or f"{name_en} flow converted to ILCD JSON.", "@xml:lang": "en"},
                            {"#text": f"{name_zh} 流已转换为 ILCD JSON。", "@xml:lang": "zh"}
                        ],
                        "common:other": {
                            "sourceSystem": src_dict.get("@type", "Flow"),
                            "isInfrastructureFlow": src_dict.get("isInfrastructureFlow", False)
                        }
                    },
                    "quantitativeReference": {"referenceToReferenceFlowProperty": "0"}
                },
                "modellingAndValidation": {
                    "LCIMethod": {"typeOfDataSet": type_of_ds},
                    "complianceDeclarations": {
                        "compliance": {
                            "common:referenceToComplianceSystem": {
                                "@refObjectId": "d92a1a12-2545-49e2-a585-55c259997756",
                                "@version": "20.20.002",
                                "@type": "source data set",
                                "@uri": "../sources/d92a1a12-2545-49e2-a585-55c259997756.xml",
                                "common:shortDescription": {"#text": "ILCD Data Network - Entry-level", "@xml:lang": "en"}
                            },
                            "common:approvalOfOverallCompliance": "Fully compliant"
                        }
                    }
                },
                "administrativeInformation": {
                    "dataEntryBy": {
                        "common:timeStamp": _now_iso(),
                        "common:referenceToDataSetFormat": {
                            "@refObjectId": "a97a0155-0234-4b87-b4ce-a45da52f2a40",
                            "@version": "03.00.003",
                            "@type": "source data set",
                            "@uri": "../sources/a97a0155-0234-4b87-b4ce-a45da52f2a40.xml",
                            "common:shortDescription": [
                                {"#text": "ILCD format", "@xml:lang": "en"},
                                {"#text": "ILCD 数据格式", "@xml:lang": "zh"}
                            ]
                        },
                        "common:referenceToPersonOrEntityEnteringTheData": {}
                    },
                    "publicationAndOwnership": {
                        "common:dataSetVersion": "01.01.000",
                        "common:referenceToOwnershipOfDataSet": {
                            "@refObjectId": "f4b4c314-8c4c-4c83-968f-5b3c7724f6a8",
                            "@type": "contact data set",
                            "@uri": "../contacts/f4b4c314-8c4c-4c83-968f-5b3c7724f6a8.xml",
                            "@version": "01.00.000",
                            "common:shortDescription": [
                                {"#text": "Tiangong LCA Data Working Group", "@xml:lang": "en"},
                                {"#text": "天工LCA数据团队", "@xml:lang": "zh"}
                            ]
                        },
                        "common:referenceToPrecedingDataSetVersion": {}
                    }
                },
                "flowProperties": {
                    "flowProperty": {
                        "@dataSetInternalID": "0",
                        "referenceToFlowPropertyDataSet": {
                            "@refObjectId": mass_prop_uuid,
                            "@type": "flow property data set",
                            "@uri": f"../flow_properties/{mass_prop_uuid}.xml",
                            "@version": "03.00.003",
                            "common:shortDescription": [
                                {"#text": "Mass", "@xml:lang": "en"},
                                {"#text": "Masse", "@xml:lang": "de"},
                                {"#text": "质量", "@xml:lang": "zh"}
                            ]
                        },
                        "meanValue": "1.0"
                    }
                }
            }
        }
    ]
    return ilcd

def batch_convert_flows_inplace(flows_dir: Path) -> int:
    """将 flows_dir 下的 *.json 全部转换为 ILCD Flow，并覆盖保存同名文件。"""
    if not flows_dir.exists():
        print(f"[2/5] flows 目录不存在，跳过：{flows_dir}")
        return 0
    n = 0
    for p in flows_dir.glob("*.json"):
        try:
            src = _load_json(p)
            ilcd = convert_flow_one(src)
            _dump_json(ilcd, p)  
            n += 1
        except Exception as e:
            print(f"[WARN][flows] 转换失败 {p.name}: {e}")
    print(f"[2/5] flows 转换完成：{n} 个文件")
    return n


def jsonld_to_ilcd_process(jsonld_data):
    """将 JSON-LD (Ecoinvent/openLCA) 转为 ILCD Process JSON（顶层对象），外层写入数组。"""
    process_uuid = jsonld_data.get("@id", "") or _uuid()
    process_name = jsonld_data.get("name", "") or "Unnamed process"
    process_desc = jsonld_data.get("description", "") or ""

    ilcd = {
        "processDataSet": {
            "@xmlns:common": "http://lca.jrc.it/ILCD/Common",
            "@xmlns": "http://lca.jrc.it/ILCD/Process",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@version": "1.1",
            "@locations": "../ILCDLocations.xml",
            "@xsi:schemaLocation": "http://lca.jrc.it/ILCD/Process ../../schemas/ILCD_ProcessDataSet.xsd",
            "processInformation": {
                "dataSetInformation": {
                    "common:UUID": process_uuid,
                    "name": {"baseName": [{"#text": process_name, "@xml:lang": "en"}]},
                    "common:generalComment": [{"#text": process_desc, "@xml:lang": "en"}]
                },
                "quantitativeReference": {"@type": "Reference flow(s)"}
            },
            "exchanges": {"exchange": []}
        }
    }

    for exc in (jsonld_data.get("exchanges", []) or []):
        exc_id = str(exc.get("internalId", "")) or _uuid()
        exc_dir = "Input" if exc.get("isInput", False) else "Output"
        amount = str(exc.get("amount", ""))
        flow = exc.get("flow", {}) or {}

        ilcd_exchange = {
            "@dataSetInternalID": exc_id,
            "referenceToFlowDataSet": {
                "@type": "flow data set",
                "@refObjectId": flow.get("@id", ""),
                "@uri": f"../flows/{flow.get('@id','')}.xml",
                "common:shortDescription": [{"#text": flow.get("name", ""), "@xml:lang": "en"}]
            },
            "exchangeDirection": exc_dir,
            "meanAmount": amount,
            "resultingAmount": amount,
            "dataDerivationTypeStatus": "Calculated"
        }

        if exc.get("isQuantitativeReference", False):
            ilcd["processDataSet"]["processInformation"]["quantitativeReference"]["referenceToReferenceFlow"] = exc_id

        ilcd["processDataSet"]["exchanges"]["exchange"].append(ilcd_exchange)

    return ilcd

def batch_convert_processes_inplace(processes_dir: Path) -> int:
    """将 processes_dir 下的 *.json 全部转换为 ILCD Process，并覆盖保存同名文件。"""
    if not processes_dir.exists():
        print(f"[3/5] processes 目录不存在，跳过：{processes_dir}")
        return 0
    n = 0
    for p in processes_dir.glob("*.json"):
        try:
            src = _load_json(p)
            ilcd = jsonld_to_ilcd_process(src)
            _dump_json([ilcd], p)  
            n += 1
        except Exception as e:
            print(f"[WARN][processes] 转换失败 {p.name}: {e}")
    print(f"[3/5] processes 转换完成：{n} 个文件")
    return n



def _guess_year_from_iso(iso_ts: str) -> str:
    try:
        return str(datetime.fromisoformat(iso_ts.replace("Z", "+00:00")).year)
    except Exception:
        return str(datetime.utcnow().year)

def _split_category_to_classes(cat: str):
    if not cat:
        return []
    parts = [p.strip() for p in cat.split("/") if p.strip()]
    return [{"@level": str(i), "@classId": "", "#text": parts[i]} for i in range(len(parts))]

def _default_node_style():
    return {
        "body": {"rx": 6, "ry": 6, "fill": "#ffffff", "stroke": "#5c246a", "strokeWidth": 1},
        "label": {"fill": "#000", "refX": 0.5, "refY": 8, "textAnchor": "middle", "textVerticalAnchor": "top"}
    }

def _port_groups():
    return {
        "groupInput": {
            "attrs": {
                "text": {"fill": "rgba(0,0,0,0.45)", "fontSize": 14},
                "circle": {"r": 4, "fill": "#fff", "magnet": True, "stroke": "#5c246a", "strokeWidth": 1}
            },
            "label": {"position": {"name": "right"}},
            "position": {"name": "absolute"}
        },
        "groupOutput": {
            "attrs": {
                "text": {"fill": "rgba(0,0,0,0.45)", "fontSize": 14},
                "circle": {"r": 4, "fill": "#fff", "magnet": True, "stroke": "#5c246a", "strokeWidth": 1}
            },
            "label": {"position": {"name": "left"}},
            "position": {"name": "absolute"}
        }
    }

def _flow_label(flow: dict) -> str:
    if not flow:
        return ""
    n = flow.get("name", "").strip()
    u = flow.get("refUnit", "").strip()
    return f"{n} [{u}]" if (n and u) else (n or u or "")

def convert_openlca_productsystem_to_template(
    src_json: dict,
    version: str,
    title_zh: str = None,
    title_en: str = None,
    mix_type_zh: str = "生产混合，在工厂",
    mix_type_en: str = "production mix, at plant",
    locale_code: str = "CHN",
    edge_dir: str = "auto",
) -> dict:
    ps = src_json
    ps_id = ps.get("@id") or ps.get("id") or _uuid()
    ps_name = ps.get("name") or "Unnamed product system"
    description = ps.get("description", "")
    category = ps.get("category", "")
    version_src = ps.get("version") or "01.01.000"
    last_change = ps.get("lastChange") or datetime.utcnow().isoformat()

    title_en = title_en or ps_name
    title_zh = title_zh or ps_name

    processes = ps.get("processes", [])
    proc_by_id = {p.get("@id") or p.get("id"): p for p in processes if (p.get("@id") or p.get("id"))}
    internal_id_map = {pid: str(i + 1) for i, pid in enumerate(proc_by_id.keys())}

    ref_process_id = None
    if isinstance(ps.get("refProcess"), dict):
        ref_process_id = ps["refProcess"].get("@id")

    x_nodes, x_edges = [], []
    in_port_count = defaultdict(int)
    out_port_count = defaultdict(int)

    cols = 3
    gap_x, gap_y = 360, 160
    base_x, base_y = 190, 180
    node_cell_id_map = {}
    node_ports_map = defaultdict(lambda: {"items": [], "groups": _port_groups()})

   
    for pid, idx_str in internal_id_map.items():
        p = proc_by_id[pid]
        cell_id = _uuid()
        node_cell_id_map[pid] = cell_id

        i = int(idx_str) - 1
        x = base_x + (i % cols) * gap_x
        y = base_y + (i // cols) * gap_y

        pname = p.get("name", "process")
        pcat = p.get("category", "")
        route_en = (pcat.split("/")[-1] if pcat else "process route")
        route_zh = route_en

        short_desc = _text_lang(f"{pname}; {route_zh}; {mix_type_zh}", f"{pname}; {route_en}; {mix_type_en}")

        node = {
            "x": x, "y": y, "id": cell_id,
            "data": {
                "id": pid,
                "label": {
                    "baseName": _text_lang(pname, pname),
                    "mixAndLocationTypes": _text_lang(mix_type_zh, mix_type_en),
                    "treatmentStandardsRoutes": _text_lang(route_zh, route_en)
                },
                "version": version,
                "shortDescription": short_desc,
                "quantitativeReference": "1" if pid == ref_process_id else "0"
            },
            "attrs": _default_node_style(),
            "label": short_desc[0]["#text"],
            "ports": {"items": [], "groups": _port_groups()},
            "shape": "rect",
            "width": 350,
            "height": 110,
            "selected": False
        }
        x_nodes.append(node)

    in_conns  = defaultdict(list)
    out_conns = defaultdict(list)

    links = ps.get("processLinks", []) or []

    def _decide_direction(provider, consumer, flow_type: str):
        ft = (flow_type or "").upper()
        if edge_dir == "ptc":
            return provider, consumer, "Output", "Input"
        if edge_dir == "ctp":
            return consumer, provider, "Input", "Output"
        if ft == "WASTE_FLOW":
            return consumer, provider, "Input", "Output"
        else:
            return provider, consumer, "Output", "Input"

    for link in links:
        provider = (link.get("provider") or {}).get("@id")
        consumer = (link.get("process")  or {}).get("@id")
        if not provider or not consumer:
            continue

        flow   = (link.get("flow") or {})
        f_uuid = flow.get("@id") or _uuid()
        f_type = flow.get("flowType") or ""
        f_label= _flow_label(flow)
        exch   = link.get("exchange") or {}
        exch_id= exch.get("internalId")

        out_idx = out_port_count[provider]
        node_ports_map[provider]["items"].append({
            "id": f"Output:{out_idx}:{f_uuid}",
            "args": {"x": "100%", "y": 70 + out_idx*22},
            "data": {
                "flowUUID": f_uuid,
                "exchangeInternalId": exch_id,
                "textLang": _text_lang(f"{f_label}；输出", f"{f_label} ; output")
            },
            "attrs": {"text": {"text": (f_label or f"输出 {out_idx}")}},
            "group": "groupOutput"
        })
        out_port_count[provider] += 1


        in_idx = in_port_count[consumer]
        node_ports_map[consumer]["items"].append({
            "id": f"Input:{in_idx}:{f_uuid}",
            "args": {"x": 0, "y": 70 + in_idx*22},
            "data": {
                "flowUUID": f_uuid,
                "exchangeInternalId": exch_id,
                "textLang": _text_lang(f"{f_label}；流入", f"{f_label} ; input")
            },
            "attrs": {"text": {"text": (f_label or f"流入 {in_idx}")}},
            "group": "groupInput"
        })
        in_port_count[consumer] += 1

        out_conns[provider].append({"@flowUUID": f_uuid, "downstreamProcess": {"@flowUUID": f_uuid, "@id": internal_id_map.get(consumer)}})
        in_conns[consumer].append({"@flowUUID": f_uuid, "upstreamProcess": {"@flowUUID": f_uuid, "@id": internal_id_map.get(provider)}})

        src_pid, tgt_pid, src_kind, tgt_kind = _decide_direction(provider, consumer, f_type)

        src_port = f"Input:{in_idx}:{f_uuid}" if src_kind == "Input" else f"Output:{out_idx}:{f_uuid}"

        tgt_port = f"Input:{in_port_count[tgt_pid]-1}:{f_uuid}" if tgt_kind == "Input" else f"Output:{out_port_count[tgt_pid]-1}:{f_uuid}"

        eid = _uuid()
        x_edges.append({
            "id": eid,
            "data": {
                "node": {
                    "sourceNodeID": node_cell_id_map.get(src_pid),
                    "targetNodeID": node_cell_id_map.get(tgt_pid),
                    "sourceProcessId": src_pid,
                    "targetProcessId": tgt_pid,
                    "sourceProcessVersion": version,
                    "targetProcessVersion": version
                },
                "connection": {
                    "flowUUID": f_uuid,
                    "flowName": flow.get("name", ""),
                    "refUnit": flow.get("refUnit", ""),
                    "flowType": f_type,
                    "exchangeInternalId": exch_id
                }
            },
            "attrs": {"line": {"stroke": "#5c246a"}},
            "shape": "edge",
            "source": {"cell": node_cell_id_map.get(src_pid), "port": src_port},
            "target": {"cell": node_cell_id_map.get(tgt_pid), "port": tgt_port},
            "zIndex": 8
        })

    for n in x_nodes:
        pid = n["data"]["id"]
        if pid in node_ports_map:
            n["ports"] = node_ports_map[pid]

    def _one_or_many(arr):
        if not arr:
            return None
        return arr[0] if len(arr) == 1 else arr

    process_instances = []
    for pid, idx_str in internal_id_map.items():
        p = proc_by_id[pid]
        pname = p.get("name", "process")
        pcat = p.get("category", "")
        route_en = (pcat.split("/")[-1] if pcat else "process route")
        route_zh = route_en
        short_desc = _text_lang(f"{pname}; {route_zh}; {mix_type_zh}", f"{pname}; {route_en}; {mix_type_en}")
        inst = {
            "@dataSetInternalID": idx_str,
            "referenceToProcess": {
                "@refObjectId": pid,
                "@type": "process data set",
                "@uri": f"../processes/{pid}.xml",
                "@version": version,
                "common:shortDescription": short_desc
            }
        }
        conns = {}
        if in_conns.get(pid):
            conns["inputExchange"] = _one_or_many(in_conns[pid])
        if out_conns.get(pid):
            conns["outputExchange"] = _one_or_many(out_conns[pid])
        if conns:
            inst["connections"] = conns
        process_instances.append(inst)

    classification = _split_category_to_classes(category)
    lcmds = {
        "lifeCycleModelDataSet": {
            "@xmlns": "http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017",
            "@xmlns:acme": "http://acme.com/custom",
            "@xmlns:common": "http://lca.jrc.it/ILCD/Common",
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@locations": "../ILCDLocations.xml",
            "@version": "1.1",
            "@xsi:schemaLocation": "http://eplca.jrc.ec.europa.eu/ILCD/LifeCycleModel/2017 ../../schemas/ILCD_LifeCycleModelDataSet.xsd",
            "lifeCycleModelInformation": {
                "dataSetInformation": {
                    "common:UUID": ps_id,
                    "name": {
                        "baseName": _text_lang(title_zh, title_en),
                        "treatmentStandardsRoutes": _text_lang(
                            category.split("/")[-1] if category else "process route",
                            category.split("/")[-1] if category else "process route"
                        ),
                        "mixAndLocationTypes": _text_lang(mix_type_zh, mix_type_en)
                    },
                    "classificationInformation": {"common:classification": {"common:class": classification}},
                    "referenceToResultingProcess": {},
                    "common:generalComment": _text_lang(description or "无", description or "N/A"),
                    "referenceToExternalDocumentation": {}
                },
                "quantitativeReference": {"referenceToReferenceProcess": internal_id_map.get(ref_process_id, "1")},
                "time": {"common:referenceYear": _guess_year_from_iso(last_change)},
                "geography": {"locationOfOperationSupplyOrProduction": {"@location": locale_code}},
                "technology": {
                    "technologyDescriptionAndIncludedProcesses": _text_lang(
                        f"{title_zh} 的过程系统与包含子过程映射由脚本自动生成。",
                        f"Process system for {title_en} with included sub-process mapping generated by script."
                    ),
                    "referenceToTechnologyFlowDiagrammOrPicture": {},
                    "processes": {"processInstance": process_instances},
                    "referenceToDiagram": {}
                },
                "mathematicalRelations": {"variableParameter": {}}
            },
            "modellingAndValidation": {
                "LCIMethodAndAllocation": {"typeOfDataSet": "Partly terminated system", "LCIMethodPrinciple": "Attributional"},
                "dataSourcesTreatmentAndRepresentativeness": {
                    "dataCutOffAndCompletenessPrinciples": _text_lang(
                        "所有主要原材料和基本能源都包括在内。小于 1% 的可忽略流被截断。危险物质不适用截断标准。",
                        "All major raw materials and essential energy are included. Flows <1% may be cut off. Hazardous substances are not subject to cut-off."
                    ),
                    "referenceToDataSource": {}
                },
                "completeness": {"completenessElementaryFlows": {}}
            },
            "administrativeInformation": {
                "common:commissionerAndGoal": {
                    "common:referenceToCommissioner": {},
                    "common:intendedApplications": _text_lang(
                        f"{title_zh} 的环境影响核算与数据连接验证。",
                        f"Environmental impact accounting and linkage validation for {title_en}."
                    )
                },
                "dataGenerator": {"common:referenceToPersonOrEntityGeneratingTheDataSet": {}},
                "dataEntryBy": {
                    "common:timeStamp": _now_iso(),
                    "common:referenceToDataSetFormat": {
                        "@refObjectId": _uuid(),
                        "@type": "source data set",
                        "@uri": "../sources/ilcd_format.xml",
                        "@version": "03.00.003",
                        "common:shortDescription": {"#text": "ILCD format", "@xml:lang": "en"}
                    },
                    "common:referenceToConvertedOriginalDataSetFrom": {},
                    "common:referenceToPersonOrEntityEnteringTheData": {}
                },
                "publicationAndOwnership": {
                    "common:dataSetVersion": version or version_src,
                    "common:permanentDataSetURI": "",
                    "common:referenceToOwnershipOfDataSet": {},
                    "common:copyright": "No",
                    "common:referenceToEntitiesWithExclusiveAccess": {},
                    "common:licenseType": "Free of charge for all users and uses"
                }
            }
        },
        "json_tg": {"xflow": {"edges": x_edges, "nodes": x_nodes}}
    }
    return lcmds

def _ensure_min_placeholders(lcmds_obj: dict, version: str):
    ds = lcmds_obj.get("lifeCycleModelDataSet", {})
    info = ds.get("lifeCycleModelInformation", {})
    adm  = ds.get("administrativeInformation", {})
    mv   = ds.get("modellingAndValidation", {})

    data_info = info.get("dataSetInformation", {})
    if not _is_uuid_like(data_info.get("common:UUID", "")):
        data_info["common:UUID"] = _uuid()

    name = data_info.get("name", {})
    name.setdefault("baseName", [{"#text": "Unnamed", "@xml:lang": "en"}])
    name.setdefault("treatmentStandardsRoutes", [{"#text": "process route", "@xml:lang": "en"}])
    name.setdefault("mixAndLocationTypes", [{"#text": "production mix, at plant", "@xml:lang": "en"}])
    data_info["name"] = name

    cls = data_info.get("classificationInformation", {}).get("common:classification")
    if not cls:
        data_info.setdefault("classificationInformation", {}).setdefault("common:classification", {})["common:class"] = []
    info["dataSetInformation"] = data_info

    tech = info.get("technology", {})
    pis = tech.get("processes", {}).get("processInstance", [])
    valid_ids = {pi.get("@dataSetInternalID") for pi in pis}
    qref = info.get("quantitativeReference", {})
    internal_id = str(qref.get("referenceToReferenceProcess", "1"))
    if internal_id not in valid_ids and valid_ids:
        qref["referenceToReferenceProcess"] = sorted(
            valid_ids, key=lambda x: int(re.sub(r"\\D", "0", x))
        )[0]
    info["quantitativeReference"] = qref
    ds["lifeCycleModelInformation"] = info

    if "dataSourcesTreatmentAndRepresentativeness" not in mv:
        mv["dataSourcesTreatmentAndRepresentativeness"] = {}
    if not mv["dataSourcesTreatmentAndRepresentativeness"].get("referenceToDataSource"):
        mv["dataSourcesTreatmentAndRepresentativeness"]["referenceToDataSource"] = {
            "@type": "source data set",
            "@version": "01.00.000",
            "@refObjectId": _uuid(),
            "@uri": "../sources/placeholder_source.xml",
            "common:shortDescription": [{"#text": "Placeholder source", "@xml:lang": "en"}]
        }
    ds["modellingAndValidation"] = mv

    comm_goal = adm.get("common:commissionerAndGoal", {})
    comm_goal.setdefault("common:referenceToCommissioner", {})
    comm_goal.setdefault("common:intendedApplications", [{"#text": "Environmental impact accounting", "@xml:lang": "en"}])
    adm["common:commissionerAndGoal"] = comm_goal

    data_entry = adm.get("dataEntryBy", {})
    data_entry.setdefault("common:referenceToDataSetFormat", {
        "@refObjectId": _uuid(),
        "@type": "source data set",
        "@uri": "../sources/ilcd_format.xml",
        "@version": "03.00.003",
        "common:shortDescription": {"#text": "ILCD format", "@xml:lang": "en"}
    })
    adm["dataEntryBy"] = data_entry

    pub = adm.get("publicationAndOwnership", {})
    pub.setdefault("common:dataSetVersion", version)
    pub.setdefault("common:permanentDataSetURI", "")
    pub.setdefault("common:copyright", "No")
    pub.setdefault("common:licenseType", "Free of charge for all users and uses")
    adm["publicationAndOwnership"] = pub

    lcmds_obj["lifeCycleModelDataSet"] = ds
    return lcmds_obj

def _wrap_as_array_if_needed(obj):
    return obj if isinstance(obj, list) else [obj]

def batch_convert_lifecyclemodels_inplace(lifecycle_dir: Path, version: str, edge_dir: str, locale: str) -> int:
    """将 lifecyclemodels/*.json 转为 ILCD LifeCycleModelDataSet + json_tg.xflow，覆盖保存同名文件。"""
    if not lifecycle_dir.exists():
        print(f"[4/5] lifecyclemodels 目录不存在，跳过：{lifecycle_dir}")
        return 0
    n = 0
    for p in lifecycle_dir.glob("*.json"):
        try:
            src_json = _load_json(p)
            out_json = convert_openlca_productsystem_to_template(
                src_json,
                version=version,
                title_zh=None,
                title_en=None,
                mix_type_zh="生产混合，在工厂",
                mix_type_en="production mix, at plant",
                locale_code=locale,
                edge_dir=edge_dir,
            )
            out_json = _ensure_min_placeholders(out_json, version)
            out_json = _wrap_as_array_if_needed(out_json)
            _dump_json(out_json, p)  
            n += 1
        except Exception as e:
            print(f"[WARN][lifecyclemodels] 转换失败 {p.name}: {e}")
    print(f"[4/5] lifecyclemodels 转换完成：{n} 个文件")
    return n


def _validate_flow_json(obj) -> bool:
    try:
        if not isinstance(obj, list) or not obj:
            return False
        root = obj[0]
        return "flowDataSet" in root and "flowInformation" in root["flowDataSet"]
    except Exception:
        return False

def _validate_process_json(obj) -> bool:
    try:
        if not isinstance(obj, list) or not obj:
            return False
        root = obj[0]
        return "processDataSet" in root and "processInformation" in root["processDataSet"]
    except Exception:
        return False

def _validate_lcmds_json(obj) -> bool:
    try:
        if not isinstance(obj, list) or not obj:
            return False
        root = obj[0]
        return "lifeCycleModelDataSet" in root and "json_tg" in root
    except Exception:
        return False

def certify(out_root: Path, counts: dict) -> Path:
    """轻量级认证：校验结构 + 计算 SHA256，输出 manifest JSON。"""
    manifest = {
        "src_root": None,  
        "out_root": str(out_root),
        "timestamp": _now_iso(),
        "counts": counts,
        "files": []
    }
    ok = True

    for sub, validator in [
        ("flows", _validate_flow_json),
        ("processes", _validate_process_json),
        ("lifecyclemodels", _validate_lcmds_json),
    ]:
        pdir = out_root / "data" / sub
        if not pdir.exists():
            continue
        for p in sorted(pdir.glob("*.json")):
            try:
                obj = _load_json(p)
                valid = validator(obj)
                sha = _sha256_file(p)
                manifest["files"].append({"path": str(p.relative_to(out_root)), "sha256": sha, "valid": bool(valid)})
                if not valid:
                    ok = False
            except Exception as e:
                manifest["files"].append({"path": str(p.relative_to(out_root)), "sha256": None, "valid": False, "error": str(e)})
                ok = False

    manifest["certified"] = bool(ok)
    out_path = out_root / "convert_manifest.json"
    _dump_json(manifest, out_path)
    print(f"[5/5] 认证 {'通过' if ok else '未通过(存在问题)'}：{out_path}")
    return out_path



def main():
    ap = argparse.ArgumentParser(prog="convert_ilcd_flow.py", description="重组目录并批量将 openLCA/Ecoinvent JSON 转为 ILCD-JSON（覆盖保存）+ 认证清单。")
    ap.add_argument("--src", dest="src_root", required=True, help="原始根文件夹路径")
    ap.add_argument("--out", dest="out_root", required=True, help="输出根文件夹路径（将创建/覆盖其中同名文件）")
    ap.add_argument("--version", default="01.01.000", help="版本号（默认 01.01.000）")
    ap.add_argument("--edge_dir", choices=["auto", "ctp", "ptc"], default="auto", help="流程图连线方向逻辑（默认 auto）")
    ap.add_argument("--locale", default="CHN", help="地理位置代码，如 CHN / CN-SD-TNA（默认 CHN）")
    ap.add_argument("--no-cert", dest="no_cert", action="store_true", help="跳过认证（默认进行）")

    args = ap.parse_args()

    src_root = Path(args.src_root).resolve()
    out_root = Path(args.out_root).resolve()
    if not src_root.exists():
        print(f"[ERROR] 源路径不存在：{src_root}", file=sys.stderr)
        sys.exit(2)


    regroup_folders(src_root, out_root)


    flows_dir = out_root / "data" / "flows"
    n_flows = batch_convert_flows_inplace(flows_dir)


    procs_dir = out_root / "data" / "processes"
    n_procs = batch_convert_processes_inplace(procs_dir)


    lcm_dir = out_root / "data" / "lifecyclemodels"
    n_lcmds = batch_convert_lifecyclemodels_inplace(lcm_dir, version=args.version, edge_dir=args.edge_dir, locale=args.locale)


    if not args.no_cert:
        manifest_path = certify(out_root, {"flows": n_flows, "processes": n_procs, "lifecyclemodels": n_lcmds})

        try:
            manifest = _load_json(manifest_path)
            manifest["src_root"] = str(src_root)
            _dump_json(manifest, manifest_path)
        except Exception:
            pass

    print("✔ 全部处理完成。")

if __name__ == "__main__":
    main()
