## shutdown
```bash
sudo shutdown -P now
```

## Router website
`192.168.11.1`

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
scp -r src pi@192.168.11.11:arir
```

```bash
scp -r testing pi@192.168.11.11:testing
```

## Pip dependencies
1. *On laptop, connected to internet*
```bash
mkdir dependencies
python3 -m pip download -r requirements.txt -d "./dependencies"
tar cvfz dependencies.tar.gz dependencies
```

2. *On same wifi as robot* Copy `dependencies` tar using scp.
```bash
scp dependencies.tar.gz pi@192.168.11.11:dependencies.tar.gz
```

3. *On robot*
```bash
tar zxvf dependencies.tar.gz
cd dependencies
python3 -m pip install * -f ./ --no-index --no-deps
```

### Troubleshooting
1. May need to use `python3 -m pip ...` to target Python3 pip environment`
2. May need to manually install setuptools, setuptools_scm, wheel and tomli before being able to run wildcard install. Wildcard install is alphabetical(?), so some packages may attempt install before dependencies and fail, requiring manual direction to install packages in order.
3. If encountering continued issues with requiring additional dependencies, try running with `--no-deps` flag.