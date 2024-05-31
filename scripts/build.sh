cd $(dirname "$(realpath "$0")")/../
rm -rf build/ dist/ captacity.egg-info/
./setup.py sdist bdist_wheel
