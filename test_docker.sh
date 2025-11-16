docker image rm -f valhalla-test | true
echo "Deleted old test image"
docker build -t valhalla-test --no-cache .
docker run valhalla-test