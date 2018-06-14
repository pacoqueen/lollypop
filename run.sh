ninja -C build install
echo "Killing lollypop-portal"
kill -9 $(ps uax | grep lollypop-portal | grep python | awk '{print $2}')
echo "Running lollypop"
# lollypop -e
# lollypop -d
lollypop
