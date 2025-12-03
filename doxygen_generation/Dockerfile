##
## EPITECH PROJECT, 2024
## my_zappy
## File description:
## Dockerfile
##

# Use a base image with necessary dependencies
FROM fedora:44

# The environment setup
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    PATH="/usr/local/texlive/2025/bin/x86_64-linux:$PATH" \
    ghost_version=10.06.0 \
    doxygen_version=1.15.0 \
    c_green="\033[0;32m" \
    c_red="\033[0;31m" \
    c_yellow="\033[0;33m" \
    c_blue="\033[0;34m" \
    c_cyan="\033[0;36m" \
    c_pink="\033[0;35m" \
    c_reset="\033[0m"   \
    init_aliases=/etc/my_alias

# Define aliases
RUN echo -e "${c_cyan}Creating aliases${c_reset}" \
    && alias_bash="my_alias_creator.sh" \
    && alias_file="/etc/my_alias" \
    && echo '#!/bin/bash' >$alias_bash \
    && echo "alias_file='$alias_file'" >>$alias_bash \
    && echo -e "if [ -f $alias_file ]; then\n        . $alias_file\nfi" >> /etc/bashrc \
    && echo 'aliases=(' >>$alias_bash \
    && echo "\"p='pwd'\"" >>$alias_bash \
    && echo "\"vi='vim'\"" >>$alias_bash \
    && echo "\"c='clear'\"" >>$alias_bash \
    && echo "\"..='cd ..'\"" >>$alias_bash \
    && echo "\"df='df -h'\"" >>$alias_bash \
    && echo "\"du='du -h'\"" >>$alias_bash \
    && echo "\"ll='ls -l'\"" >>$alias_bash \
    && echo "\"la='ls -la'\"" >>$alias_bash \
    && echo "\"h='history'\"" >>$alias_bash \
    && echo "\"ga='git add'\"" >>$alias_bash \
    && echo "\"gd='git diff'\"" >>$alias_bash \
    && echo "\"...='cd ../..'\"" >>$alias_bash \
    && echo "\"cecho='echo -e'\"" >>$alias_bash \
    && echo "\"necho='echo -n'\"" >>$alias_bash \
    && echo "\"gcl='git clone'\"" >>$alias_bash \
    && echo "\"gc='git commit'\"" >>$alias_bash \
    && echo "\"gb='git branch'\"" >>$alias_bash \
    && echo "\"gs='git status'\"" >>$alias_bash \
    && echo "\"neecho='echo -ne'\"" >>$alias_bash \
    && echo "\"....='cd ../../..'\"" >>$alias_bash \
    && echo "\"gco='git checkout'\"" >>$alias_bash \
    && echo "\"grep='grep --color=auto'\"" >>$alias_bash \
    && echo "\"gcm='git commit -m'\"" >>$alias_bash \
    && echo "\"gl='git shortlog'\"" >>$alias_bash \
    && echo "\"gls='git shortlog -sn'\"" >>$alias_bash \
    && echo "\"gl='git log --oneline --decorate'\"" >>$alias_bash \
    && echo "\"glo='git log --oneline --decorate --graph'\"" >>$alias_bash \
    && echo "\"gloa='git log --oneline --decorate --graph --all'\"" >>$alias_bash \
    && echo ')' >>$alias_bash \
    && echo "echo -e \"${c_pink}Adding aliases${c_reset}\"" >>$alias_bash \
    && echo "echo '' > $alias_file" >>$alias_bash \
    && echo 'for alias_cmd in "${aliases[@]}"; do' >>$alias_bash \ 
    && echo "echo -e \"${c_pink}Adding alias '\$alias_cmd'${c_reset}\"" >>$alias_bash \
    && echo 'echo "alias $alias_cmd" >> $alias_file' >>$alias_bash \
    && echo "echo -e \"${c_green}Added alias '\$alias_cmd' successfully${c_reset}\"" >>$alias_bash \
    && echo 'done' >>$alias_bash \
    && chmod +x $alias_bash \
    && ./$alias_bash \
    && chmod a+x $alias_file \
    && echo -e "${c_green}Aliases created successfully${c_reset}"

# Custom colour rebind
RUN echo '#!/bin/bash' >/bin/cecho && echo "echo -e \$@" >>/bin/cecho && chmod +x /bin/cecho

# Update the system and install necessary packages
RUN cecho "${c_cyan}Updating cache ...${c_reset}" \
    && dnf makecache --refresh \
    && dnf update -y \
    && cecho "${c_green}Cache updated successfully${c_reset}"

# Install Doxygen dependencies
RUN cecho "${c_cyan}Installing Doxygen dependencies ...${c_reset}" \
    && dnf install -y \
    qt  \
    tar \
    git \
    gzip \
    less \
    wget \
    curl \
    flex \
    make \
    bison \
    glibc \
    cmake \
    mathjax \
    doxygen \
    graphviz \
    qt-devel \
    qt5-qtbase \
    bison-devel \
    glibc-devel \
    qt5-qttools \
    perl-Digest-MD5 \
    qt5-qtbase-devel \
    qt5-qtsvg-devel \
    qt5-qttools-devel \
    qt5-qttools-static \
    glibc-all-langpacks \
    java-latest-openjdk \
    java-latest-openjdk-headless \
    && cecho "${c_green}Doxygen dependencies installed successfully${c_reset}"

# Install texlive
RUN cecho "${c_cyan}Installing texlive ...${c_reset}" \
    && cd /tmp \
    && curl -LO -o install-tl-unx.tar.gz https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
    && zcat < install-tl-unx.tar.gz | tar xf - \
    && cd install-tl-*/ \
    && perl ./install-tl --no-interaction \
    && cecho "${c_green}Texlive installed successfully${c_reset}"


# Install Ghostscript and GhostPDL (download once, reuse archives)
RUN cecho "${c_cyan}Installing Ghostscript and GhostPDL (cached downloads)...${c_reset}" \
    && cd /tmp \
    && mkdir -p /tmp/downloads /tmp/ghostscript_installation \
    && cd /tmp/downloads \
    && curl -L -o ghostscript-${ghost_version}.tar.gz https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/ghostscript-${ghost_version}.tar.gz \
    && curl -L -o ghostpdl-${ghost_version}.tar.gz https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10060/ghostpdl-${ghost_version}.tar.gz \
    && cd /tmp/ghostscript_installation \
    && tar -xvf /tmp/downloads/ghostscript-${ghost_version}.tar.gz \
    && cd ghostscript-${ghost_version} \
    && ./configure \
    && make -j$(nproc) \
    && make install \
    && cd /tmp/ghostscript_installation \
    && tar -xvf /tmp/downloads/ghostpdl-${ghost_version}.tar.gz -C /tmp/ghostscript_installation \
    && cd /tmp/ghostscript_installation/ghostpdl-${ghost_version} \
    && ./configure \
    && make -j$(nproc) \
    && make install \
    && cecho "${c_green}Ghostscript and GhostPDL installed successfully${c_reset}"

# Install doxygen from source
RUN cecho "${c_cyan}Installing doxygen from source ...${c_reset}" \
    && cd /tmp \
    && mkdir doxygen_installation \
    && cd doxygen_installation \
    && curl -LO https://www.doxygen.nl/files/doxygen-${doxygen_version}.src.tar.gz \
    && tar -xvf doxygen-${doxygen_version}.src.tar.gz \
    && cd doxygen-${doxygen_version} \
    && mkdir build \
    && cd build \
    && cmake -G "Unix Makefiles" .. \
    && cmake -Dbuild_wizard=YES .. \
    && make \
    && cmake -Dbuild_doc=YES .. \
    && make docs \
    && make install  \
    && cd ../../.. \
    && cecho "${c_green}Doxygen installed successfully${c_reset}"

# Install PlantUML
RUN cecho "${c_cyan}Installing PlantUML ...${c_reset}" \
    && cd /usr/local/bin \
    && curl -L -o /usr/local/bin/plantuml.jar https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar \
    && echo '#!/bin/sh' > /usr/local/bin/plantuml \
    && echo 'exec java -jar /usr/local/bin/plantuml.jar "$@"' >> /usr/local/bin/plantuml \
    && chmod +x /usr/local/bin/plantuml \
    && cecho "${c_green}PlantUML installed successfully${c_reset}"

# Clean up
RUN echo -e "${c_cyan}Cleaning up ...${c_reset}" \
    && dnf clean all \
    && rm -rf /var/cache/dnf \
    && rm -rf /tmp/* \
    && cecho "${c_green}Clean up completed successfully${c_reset}"

# Remove the temporary alias
RUN rm -f /bin/cecho

# Create a directory for the source code
WORKDIR /app
