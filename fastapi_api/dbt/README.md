# dbt Analytics Models

## Overview

This dbt project transforms raw data from the FastAPI-seeded PostgreSQL tables into clean, business-ready datasets.

## Project Structure

```
dbt/
├── dbt_project.yml       # Project configuration
├── profiles.yml          # Database connection settings
└── models/
    ├── sources.yml       # Source table definitions
    ├── staging/          # Type-safe, cleaned views
    │   ├── stg_app_profile.sql
    │   ├── stg_appointment.sql
    │   └── stg_ab_event.sql
    └── marts/            # Business logic tables
        ├── dim_patient_from_app_profiles.sql
        ├── fct_appointments.sql
        └── fct_ab_events.sql
```

## Data Lineage

```
Sources (Raw Tables)
    ↓
Staging Models (Views)
    ↓
Marts (Materialized Tables)
```

### Sources
- `public.app_profile` - Patient acquisition data
- `public.appointment` - Healthcare appointments
- `public.ab_event` - A/B test events

### Staging Models
**Materialization**: Views

- `stg_app_profile` - Cleaned app profiles with null handling
- `stg_appointment` - Type-cast appointments with proper date handling
- `stg_ab_event` - Cleaned A/B test events

### Marts
**Materialization**: Tables

- `dim_patient_from_app_profiles` - Deduplicated patient dimension
- `fct_appointments` - Appointment facts
- `fct_ab_events` - A/B test event facts

## Running dbt

### Local Development

```bash
cd dbt
export DBT_PROFILES_DIR=$(pwd)

# Install dependencies (if any)
dbt deps

# Run all models
dbt build

# Run specific models
dbt run --select stg_app_profile
dbt run --select marts.*

# Test data quality
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### Docker

```bash
# From fastapi_api/ directory
docker-compose run --rm dbt
```

## Configuration

### profiles.yml
```yaml
analytics_api:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost  # or 'db' in Docker
      user: app
      password: app
      dbname: appdb
      port: 5432
      schema: public
```

### dbt_project.yml
```yaml
models:
  analytics_api:
    +materialized: view
    staging:
      +materialized: view
    marts:
      +materialized: table
```

## Model Descriptions

### dim_patient_from_app_profiles
**Purpose**: Create a unique patient dimension from app profiles

**Logic**: Deduplicates patients using `any_value()` aggregation

**Use Cases**:
- Join with fact tables for patient attributes
- Patient segmentation analysis
- Traffic source attribution

### fct_appointments
**Purpose**: Clean appointment facts ready for analysis

**Use Cases**:
- No-show rate analysis
- Doctor utilization metrics
- Appointment volume trends

### fct_ab_events
**Purpose**: A/B test event facts

**Use Cases**:
- Conversion funnel analysis
- Test vs Control comparison
- Event timing analysis

## Adding New Models

1. **Create SQL file** in appropriate directory:
   - `staging/` for cleaning/type-casting
   - `marts/` for business logic

2. **Use dbt syntax**:
   ```sql
   {{ ref('upstream_model') }}
   {{ source('schema', 'table') }}
   ```

3. **Add tests** in schema.yml:
   ```yaml
   models:
     - name: my_new_model
       columns:
         - name: id
           tests:
             - unique
             - not_null
   ```

4. **Run and test**:
   ```bash
   dbt run --select my_new_model
   dbt test --select my_new_model
   ```

## Best Practices

1. **Staging layer**: Only type-casting and null handling, no business logic
2. **Marts layer**: Business logic, aggregations, joins
3. **Naming**: `stg_` prefix for staging, `dim_` for dimensions, `fct_` for facts
4. **Documentation**: Add descriptions in schema.yml files
5. **Testing**: Add uniqueness and not_null tests for primary keys

## Troubleshooting

### Connection Issues
```bash
# Test connection
dbt debug

# Check profiles.yml location
echo $DBT_PROFILES_DIR
```

### Model Failures
```bash
# Run with verbose logging
dbt run --select failing_model --debug

# Check compiled SQL
cat target/compiled/analytics_api/models/path/to/model.sql
```

## Integration with Airflow

```python
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='dbt_build',
    bash_command='cd /app/dbt && dbt build',
    env={'DBT_PROFILES_DIR': '/app/dbt'}
)
```

## Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [dbt Style Guide](https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md)
