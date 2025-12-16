## How to setup DDNS using Cloudflare on OpenWRT

### You first need to get an account API token that allows editting the domain you have hosted with Cloudflare.
1. https://dash.cloudflare.com/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/api-tokens
2. Click on "Create Token"
3. Click the "Use template' button next to "Edit zone DNS"
4. For "Permissions" leave it set at "Zone" -> "DNS" -> "Edit"
5. Under "Zone Resources" you can chose to allow for a single domain or set it to all domains
6. If you need to use a DDNS service you probably don't want to restrict access by IP
7. If you set the start and end restrictions, just be mindful you will need to get a new API token when the current one expires
8. Then click "Continue to summary"
9. You will be taken to the confirmation page asking that you want to create the token. Click "Create Token" when ready.
10. Make sure you record the token string in a safe place as you won't be shown it again. If you do lose it all you need to do is delete the token and request a new one so all won't be lost. Make sure you guard the token like you would a password.

### The Cloudflare DDNS scripts don't create a hostname/DNS record(s), so you need to add an A and if you want IPv6 an AAAA record for your router
1. Go into the DNS records section https://dash.cloudflare.com/xxxxxxxxxxxxxxxxxxxxxxxxx/example.com/dns/records
2. Click "Add record"
3. For IPv4 select "A" then type in the hostname, eg "router", then for the IP set it as 127.0.0.1 make sure the "Proxy status" switch is disabled and then click "Save"
4. For IPv6 select click "Add record" again, then select "AAAA" then type in the hostname again, eg "router", then for the IP set it as ::1 again make sure the "Proxy status" switch is disabled and then click "Save"

### Open the OpenWRT webUI
1. Go to the "System" menu, and click "Software"
2. Click the "Update Lists" button to make sure your router has the latest version list of available packages
3. In the "Filter:" text box type in and install the following packages
- curl
- ca-bundle
- ca-certificates
- ddns-scripts
- ddns-scripts-cloudflare
- ddns-scripts-luadns
- ddns-scripts-services
- wget

### DDNS Configuration Steps
- There should be a menu labelled "Services" in the middle at the top of the page
- Select "Dynamic DNS" from the drop down
- If there is 2 disabled Cloudflare DDNS lines, simply click edit on each and update as below, make sure you enable them
- If there isn't any DDNS services listed follow the steps below to add them
1. Click on "Add new services"
2. Give it a useful display name, eg CloudflareDDNSv4
3. Select IPv4
4. For "DDNS Service provider" select "cloudflare.com-v4", this is the Cloudflare API version, not to do with IPv4
5. Click "Create service"
6. Make sure the "Enabled" checkbox at the top is checked
7. Enter the full hostname in the "Lookup Hostname" box, eg router.example.com
8. For the domain box, you need to give the full hostname again, but with an '@' symbol instead of a '.' before the domain name, eg router@example.com
9. For the username for Cloudflare you must set it to 'Bearer'
10. You paste the API token into the "Password" box
11. It's a good idea to tick the 'Use HTTP Secure' box, as your API token will be encrypted when sent to Cloudflare
12. So curl or wget can verify they're really connection to Cloudflare servers, put /etc/ssl/certs in the "Path to CA-Certificate" text box
13. Scroll up to the top of the page and click "Advanced Settings"
14. Make sure "Network" is selected for "IP address source"
15. For "Network" select "wan" for IPv4 or "wan6" for IPv6
16. It's a good idea to set the "DNS-Server" to an external public resolver, such as 1.1.1.1 for Cloudflare's or 8.8.8.8 for Google's, because the DDNS scripts check what the IPs are in DNS before attempting to update Cloudflare
17. Change the rest of the settings to suit
18. When you're happy click "Save" at the bottom right
19. Rinse and repeat for IPv6

Don't forget to click "Save & Apply" at the bottom right

### If OpenWRT doesn't trigger an immediate update
- Click "Start DDNS"

### If after a few seconds the current IPs don't display under "router.example.com"
 - There may be a problem with your config

1. Click edit on one of the DDNS lines
2. Select the "Log File Viewer" tab at the top right of the page
3. Click the "Read / Reread log file"
4. Read through the log for any errors and make changes to the DDNS config
5. Click "Save"
6. The click "Start DDNS" again

### That's about it
