# HOW TO RUN
- Prepare environment:
    - Copy `.env.sample` to `.env`
    - Change setting in `.env`
    
- From project root:

```
python -m data_import <command>
```

- From data_import package root:

```
./bootstrap.py <command>
```

# EXAMPLE USAGE:
- **Important Note** The xlsx should disable password for importing to work normally.
- Convert XLSX to pickle:
```
./bootstrap.py xlsx-to-pickle
```

- In case there are changes in xlsx, remove XLSX pickle:
```
./bootstrap.py rm-xlsx-pickle
```

- Generate MasterData pickle:
```
./bootstrap.py gen-master --customer=True --forest=True
```

- Truncate database tables:
```
./bootstrap.py truncate-db
```

- Load to Database
```
./bootstrap.py insert-db --customer=True --forest=True
```

- Link forest and customer
```
./bootstrap.py link-forest-customer
```

- Run data migration
```
./bootstrap.py migrate --name <name>
```

*NOTE*: `name` is the file (except extension) under `migrations`

# FLOW:
- `XLSX -> pickle -> importer + converter -> intermediate pickle -> DbImporter -> DbService -> DB`

# TESTS:
- Currently the tests is integreated with Django testsuite

```
./manage.py test
```
