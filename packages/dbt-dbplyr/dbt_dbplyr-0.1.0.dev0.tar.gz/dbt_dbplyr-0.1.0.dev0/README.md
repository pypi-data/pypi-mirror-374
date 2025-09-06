# dbt-plyr
With dbt-plyr you can write your [dbt](https://www.getdbt.com/) models using [dbplyr](https://dbplyr.tidyverse.org/). You can find the full documentation [here](https://binste.github.io/dbt-plyr/intro.html).

A simple dbt-plyr model looks like this:
```python
from dbt_ibis import depends_on, ref


@depends_on(ref("stg_stores"))
def model(stores):
    return stores.filter(stores["country"] == "USA")
```

You can install `dbt-plyr` via pip or conda:
```bash
pip install dbt-plyr
# or
conda install -c conda-forge dbt-plyr
```

In addition, you'll need to install the relevant [`Ibis` backend](https://ibis-project.org/install) for your database.

You can read about the advantages of combining dbt and Ibis in [this blog post](https://ibis-project.org/posts/dbt-plyr/).


## Development
```bash
pip install -e '.[dev]'
```

You can run linters and tests with
```bash
hatch run linters
hatch run tests
```
