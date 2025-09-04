import mailbox
import sys



def main():
    filename_mbox = sys.argv[1]
    filename_id = sys.argv[2]
    id = mbox_last_id(filename_mbox)
    with open(filename_id, 'w') as f:
        f.write(id)
    print("wrote ( %s )" % id)


def mbox_last_id(filename):
    id = ""
    box = mailbox.mbox(filename, create=False)
    for msg in box:
        id = msg["message-id"].replace("\n", "").replace("\r", "").strip()
    box.close()
    return id
