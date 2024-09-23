# Use the official Orthanc image
FROM jodogne/orthanc:1.12.4

# Copy your custom Orthanc configuration file
COPY docker/orthanc.json .

# Expose the necessary ports
EXPOSE 8042 11112

# Command to run Orthanc
CMD ["./orthanc.json"]