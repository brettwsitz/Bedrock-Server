FROM ubuntu

ENV TTY=TRUE

RUN apt-get update && apt-get install -y curl unzip

RUN mkdir /server && cd /server
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

EXPOSE 19132/udp 19133/udp

CMD LD_LIBRARY_PATH=. ./bedrock_server

# Keep the container running without a process (for debugging ONLY)
# CMD tail -f /dev/null