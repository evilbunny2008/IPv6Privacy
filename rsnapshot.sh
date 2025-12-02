#!/bin/bash

# Simple script to better co-ordinate rsnapshot daily, weekly and monthly backups and then compress and email the rsync logs

# === INTERACTIVE DETECTION ===
if [ -t 1 ]; then
    INTERACTIVE=1
else
    INTERACTIVE=0
fi

# === COLOUR DEFINITIONS ===
if [ "$INTERACTIVE" = 1 ]; then
    RED="\033[31m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    CYAN="\033[36m"
    RESET="\033[0m"
else
    RED=""
    GREEN=""
    YELLOW=""
    CYAN=""
    RESET=""
fi

# === CONFIGURATION ===
REPORT_DATE="$(date '+%Y-%m-%d')"
EMAIL_TO="user@example.com"
EMAIL_SUBJECT="Rsnapshot Backup Report ${REPORT_DATE}"
TMPDIR=$(mktemp -d)
LOGFILE="$TMPDIR/rsync_${REPORT_DATE}.txt"

# GZip extension and mime type
#OUTFILE="$TMPDIR/rsync_${REPORT_DATE}.txt.gz"
#MIMETYPE="application/gzip"

# XZ extension and mime type
OUTFILE="$TMPDIR/rsync_${REPORT_DATE}.txt.xz"
MIMETYPE="application/x-xz"

DAY_OF_MONTH=$(date +%d)
DAY_OF_WEEK=$(date +%u)

log() {
    # Prints to screen (if interactive) and appends to log
    local msg="$1"
    echo -e "[$(date '+%H:%M:%S')] $msg" | tee -a "$LOGFILE"
}

log "${CYAN}Starting backup...${RESET}"

# === MONTHLY BACKUP ===
if [ "$DAY_OF_MONTH" = "01" ]; then
    log "${YELLOW}Running monthly rsnapshot...${RESET}"
    rsnapshot -V -c /etc/rsnapshot.conf monthly 2>&1 | ts '[%H:%M:%S]' | tee -a "$LOGFILE"
fi

# === WEEKLY BACKUP ===
if [ "$DAY_OF_WEEK" = "7" ]; then
    log "${YELLOW}Running weekly rsnapshot...${RESET}"
    rsnapshot -V -c /etc/rsnapshot.conf weekly 2>&1 | ts '[%H:%M:%S]' | tee -a "$LOGFILE"
fi

# === REMOTE SSH JOBS TO DUMP SQL FOR BACKUP ===
for host in \
    "root@host1.example.com:/root/backup-mariadb.sh" \
    "root@host2.example.com:/root/backup-mariadb.sh"
do
    userhost="${host%%:*}"
    cmd="${host#*:}"

    log "${CYAN}Running SSH job on $userhost...${RESET}"
    if ssh "$userhost" "$cmd" 2>&1 | tee -a "$LOGFILE"; then
        log "${GREEN}SSH job on $userhost OK${RESET}"
    else
        log "${RED}SSH job on $userhost FAILED${RESET}"
    fi
done

# === DAILY BACKUP ===
log "${YELLOW}Running daily rsnapshot...${RESET}"
rsnapshot -V -c /etc/rsnapshot.conf daily 2>&1 | ts '[%H:%M:%S]' | tee -a "$LOGFILE"

# === COMPRESS LOG ===
log "${CYAN}Compressing log...${RESET}"

# Use gzip to compress
#gzip -9 -c "$LOGFILE" > "$OUTFILE"

# Use xz to compress
xz -9 -e -z "$LOGFILE" > "$OUTFILE"

# === EMAIL SENDING ===
{
    echo "To: $EMAIL_TO"
    echo "Subject: $EMAIL_SUBJECT"
    echo "MIME-Version: 1.0"
    echo "Content-Type: multipart/mixed; boundary=\"BOUNDARY\""
    echo
    echo "--BOUNDARY"
    echo "Content-Type: text/plain; charset=UTF-8"
    echo
    echo "Rsync completed. Compressed log attached."
    echo
    echo "--BOUNDARY"
    echo "Content-Type: $MIMETYPE"
    echo "Content-Disposition: attachment; filename=\"$(basename "$OUTFILE")\""
    echo "Content-Transfer-Encoding: base64"
    echo
    base64 "$OUTFILE"
    echo "--BOUNDARY--"
} | sendmail -t

rm -rf "$TMPDIR"
