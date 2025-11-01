FROM ubuntu:22.04

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    git \
    xz-utils \
    file \
    && rm -rf /var/lib/apt/lists/*

# Install Flutter
RUN git clone https://github.com/flutter/flutter.git -b stable /usr/local/flutter
ENV PATH="$PATH:/usr/local/flutter/bin"

# Run flutter doctor to set up Flutter
RUN flutter doctor

# Copy pubspec and install dependencies
COPY pubspec.yaml /app/pubspec.yaml
RUN flutter pub get

# Copy the rest of the application
COPY . /app

# Build the executable
RUN dart compile exe bin/delta_os_core.dart

# Start command
CMD ["dart", "bin/delta_os_core.dart", "--demo"]