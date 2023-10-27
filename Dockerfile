FROM ubuntu

RUN apt-get update && apt-get install -y curl unzip python3 python3-pip
RUN pip3 install schedule google-auth google-auth-oauthlib google-api-python-client

RUN mkdir /server && mkdir /server/worlds && cd /server
WORKDIR /server

##################################################################################################################
# This command retrieves the HTML content of the Minecraft Bedrock Dedicated Server download page,
# extracts the URL for the Linux version of the server using grep, and downloads the server file using curl
# 
# This command relies on the specific HTML structure of the Minecraft download page, 
# so if the page structure changes in the future, the command may need to be adjusted accordingly
# 
# Microsoft restricts site access with curl so a user agent must be spoofed
RUN curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3" "https://www.minecraft.net/en-us/download/server/bedrock" |\
    grep -o "https://minecraft.azureedge.net/bin-linux/bedrock-server-.*\.zip" |\
    xargs curl -o bedrock-server.zip
RUN unzip bedrock-server.zip
RUN chmod +x ./bedrock_server

COPY configuration/* /server 

COPY automatic_backups/* /server
RUN chmod +x backup.py
RUN chmod +x drive.py

EXPOSE 19132/udp 19133/udp 443/tcp

CMD ["sh", "-c", "python3 backup.py & LD_LIBRARY_PATH=. ./bedrock_server"]

# Keep the container running without a process (for debugging ONLY)
# CMD tail -f /dev/null