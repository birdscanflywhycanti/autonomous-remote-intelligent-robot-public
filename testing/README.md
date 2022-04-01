## shutdown
```bash
sudo shutdown -P now
```

## ssh command usage:
*On COMP5010 router*
```bash
ssh pi@192.168.11.11
```

*On Pixel hotspot*
```bash
ssh pi@192.168.18.55
```

## scp command usage:
*Copy single file*
```bash
scp filename.py pi@192.168.11.11:folder/filename.py
```

*Copy folder (and sub-files / folders)*
```bash
scp -r folder pi@192.168.11.11:folder
```

## Pip dependencies
1. *On system with internet*
```bash
mkdir dependencies
pip download -r requirements.txt -d "./dependencies"
tar cvfz dependencies.tar.gz dependencies
```

2. Copy `dependencies` tar using scp.
```bash
scp dependencies.tar.gz pi@192.168.11.11:dependencies.tar.gz
```

3. *On system without internet*
```bash
tar zxvf dependencies.tar.gz
cd dependencies
pip install * -f ./ --no-index
```

### Troubleshooting
1. May need to use `python3 -m pip ...` to target Python3 pip environment`
2. May need to manually install setuptools, setuptools_scm, wheel and tomli before being able to run wildcard install. Wildcard install is alphabetical(?), so some packages may attempt install before dependencies and fail, requiring manual direction to install packages in order.
3. If encountering continued issues with additioanl dependencies, try running with `--no-deps` flag.