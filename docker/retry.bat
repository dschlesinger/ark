set container=mirai-dicom

docker container stop %container%

docker container rm %container%

docker images rm %container%

docker build -t %container% -f docker/%container%.Dockerfile .

docker run -d --name %container% %container%