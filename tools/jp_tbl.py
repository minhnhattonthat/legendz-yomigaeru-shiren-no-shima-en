"""Write a Thingy table of the kana codes for jp_left.py --tbl FILE --le16: python -X utf8 tools/jp_tbl.py work/jp_le16.tbl"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jpcodec  # noqa: E402

Path(sys.argv[1]).write_text("".join("%03X=%s\n" % (c, g) for c, g in sorted(jpcodec.TABLE.items()) if 1 <= c <= 0xA3), encoding="utf-8", newline="\n")
