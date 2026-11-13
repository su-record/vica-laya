"""Copy a Laya GGUF with Vica Laya names; tensors and behavioural metadata are unchanged."""
import json
import sys

import gguf
from gguf.scripts.gguf_new_metadata import MetadataDetails, copy_with_new_metadata, get_field_data

src, dst, checkpoint = sys.argv[1:4]
NAME = "vica-laya"

reader = gguf.GGUFReader(src)
spec = json.loads(get_field_data(reader, "ggmlc.graph_spec"))
spec["name"] = NAME
decision = json.loads(get_field_data(reader, "ggmlc.decision"))
decision["model_name"] = NAME
decision["checkpoint"] = checkpoint
S = gguf.GGUFValueType.STRING
new = {
    "general.name": MetadataDetails(S, NAME),
    "laya.model_name": MetadataDetails(S, NAME),
    "laya.checkpoint": MetadataDetails(S, checkpoint),
    "ggmlc.graph_spec": MetadataDetails(S, json.dumps(spec, separators=(",", ":"))),
    "ggmlc.decision": MetadataDetails(S, json.dumps(decision, separators=(",", ":"), ensure_ascii=False)),
}
writer = gguf.GGUFWriter(dst, arch=get_field_data(reader, "general.architecture"), endianess=reader.endianess)
alignment = get_field_data(reader, "general.alignment")
if alignment is not None:
    writer.data_alignment = alignment
expected = sorted(new)
copy_with_new_metadata(reader, writer, dict(new), [])

out = gguf.GGUFReader(dst)
a = {t.name: (t.tensor_type, t.data.tobytes()) for t in reader.tensors}
b = {t.name: (t.tensor_type, t.data.tobytes()) for t in out.tensors}
assert a == b, "tensor data changed"
before = {k: f.contents() for k, f in reader.fields.items() if not k.startswith("GGUF.")}
after = {k: f.contents() for k, f in out.fields.items() if not k.startswith("GGUF.")}
assert before.keys() == after.keys(), before.keys() ^ after.keys()
changed = sorted(k for k in before if before[k] != after[k])
# A model staged with these names already (from release 2026.11.13.1) comes out unchanged.
assert changed in (expected, []), changed
print(f"tensors identical: {len(a)}; metadata changed: {changed or 'none, already named'}")
