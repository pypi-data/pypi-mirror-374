from io import StringIO
import turbofm
import turbofm.scan
import mailbox
import sys
import logging
import email.generator
import re
import xler8


def html_readable(src):
    res = src.replace("<br>", " ").replace("<BR>", " ").replace("<br/>", " ").replace("<BR/>", " ")

    small_droplets = [ '<html>', '</html>', '<body>', '</body>', '&nbsp;', '<head>', '</head>', '</div>', '&quot;', '<ul>', '</ul>' ]
    for s in small_droplets:
        res = res.replace(s, ' ')
        res = res.replace(s.upper(), ' ')

    res = res.replace('<li>', '[')
    res = res.replace('</li>', ']')

    kill_meta = re.compile(r"<meta[^>]*>")
    res = re.sub(kill_meta, '', res)

    kill_div = re.compile(r"<div[^>]*>")
    res = re.sub(kill_div, ' ', res)

    reduce_space = re.compile(r" +")
    res = re.sub(reduce_space, ' ', res)

    return res.strip()




logging.basicConfig(level=logging.INFO)



if len(sys.argv) == 1:
    print("""
# usage: bodies SRC.mbox OUTFILE
""")
    sys.exit(1)


arg_infile = sys.argv[1]
logging.info("infile="+arg_infile)

arg_outfile = sys.argv[2]
logging.info("outfileprefix="+arg_outfile)

body_words_indices = None
body_words_titles = None
body_words_cws = None

sub_words_indices = None
sub_words_titles = None
sub_words_cws = None

try:
    arg_body_words_indices = sys.argv[3]
    arg_body_words_titles = sys.argv[4]
    arg_body_words_cws = sys.argv[5]
    body_words_indices = arg_body_words_indices.split(",")
    body_words_titles = arg_body_words_titles.split(",")
    body_words_cws = arg_body_words_cws.split(",")
except:
    body_words_indices = None
    body_words_titles = None
    body_words_cws = None


table_data = [ ['message_id', 'subject', 'body'] ]
if body_words_titles != None:
    table_data = [ ['message_id', 'subject', 'body'] + body_words_titles ]

table_cw = { 'A': 100, 'B': 100, 'C': 300 }
# todo table_cw erweitern assoziativ um body_words_cws

try:
    less_spaces = re.compile(r" +")
    

    with open(arg_outfile + ".txt", 'w') as outfile:

        for msg_item in turbofm.scan.scan_mbox(arg_infile):
            msg = msg_item["msg"]
            msg_id = "na"
            if "message-id" in msg:
                msg_id = msg["message-id"].replace("\r", " ").replace("\n", " ").strip()
                msg_id = re.sub(less_spaces, ' ', msg_id)
            msg_sub = "na"
            if "subject" in msg:
                msg_sub = msg["subject"].strip()
                msg_sub = re.sub(less_spaces, ' ', msg_sub)
            
            msg_body_raw = ""
            if msg.is_multipart():
                body_plain=""
                body_html=""
                for part in msg.walk():
                    if part.get_content_type()=="text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                        body_plain = part.get_payload(decode=True).decode(errors='ignore')
                    if part.get_content_type()=="text/html" and "attachment" not in str(part.get("Content-Disposition")):
                        body_html = part.get_payload(decode=True).decode(errors='ignore')
                if body_plain == "":
                    body_html = body_html.replace("\r", "").replace("\n", "").strip()
                    body_html = html_readable(body_html)
                    outfile.write(body_html)
                    msg_body_raw = body_html
                else:
                    body_plain = body_plain.replace("\r", "").replace("\n", "").strip()
                    body_plain = html_readable(body_plain)
                    outfile.write(body_plain)
                    msg_body_raw = body_plain
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
                body = body.replace("\r", "").replace("\n", "").strip()
                body = html_readable(body)
                outfile.write(body)
                msg_body_raw = body

            # text output message final
            outfile.write("\n")

            # table add whole message row
            msg_body_raw = msg_body_raw.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").strip()
            if body_words_titles != None:
                msg_body_raw_cols = msg_body_raw.split(" ")
                extra_values = [msg_body_raw_cols[int(yy)] for yy in body_words_indices ]
                table_data.append([msg_id, msg_sub, msg_body_raw] + extra_values)
            else:
                table_data.append([msg_id, msg_sub, msg_body_raw])

        # post msg loop write excel
        xler8.xlsx_out(filename=arg_outfile + ".xlsx", sheets={
            'messages': {
                'data': table_data,
                'cw': table_cw
            }
        })

except Exception as e:
    logging.error("Something went wrong (%s)" % str(e))
