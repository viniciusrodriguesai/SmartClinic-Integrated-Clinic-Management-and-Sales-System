# SmartClinic

An academic desktop application for managing customers, sellers, products and purchases with Python, Tkinter and MySQL. The graphical interface and data-access classes are present; a tracked database bootstrap and real MySQL-compatible integration checks are now provided.

## Local setup

Use Python 3, MySQL and a graphical desktop with Tkinter installed. Create and activate a virtual environment, then:

```bash
python -m pip install -r requirements.txt
cp secreto.env.example secreto.env
```

On Windows, copy the example file using your file manager or `Copy-Item`. Edit `secreto.env` with your local database connection values. That file is ignored by Git; never commit credentials.

Create an empty local MySQL database and a user with privileges on that database, then set the connection values in `secreto.env`:

```sql
CREATE DATABASE smartclinic CHARACTER SET utf8mb4;
CREATE USER 'smartclinic'@'localhost' IDENTIFIED BY 'choose_your_own_local_password';
GRANT ALL PRIVILEGES ON smartclinic.* TO 'smartclinic'@'localhost';
```

Apply the tracked schema and monthly report view:

```bash
python scripts/bootstrap_database.py
```

The bootstrap creates missing tables and the view; it does not drop data or migrate an incompatible old schema. Use a fresh demo database. The SQL defines the columns actually used by all four DAO classes, foreign keys, stock/price checks and timestamps.

## Entry points

```bash
python interface/interface.py
```

The GUI attempts to connect at startup and reports unavailable database access. A separate customer-management CLI is available:

```bash
python src/main.py
```

## Organization

- `interface/interface.py`: Tkinter GUI.
- `src/db.py`: environment loading and connection lifecycle.
- `src/cliente_dao.py`, `vendedor_dao.py`, `produto_dao.py`, `compra_dao.py`: database operations.

## Validation and next steps

The schema and two end-to-end database tests were run successfully against an isolated MariaDB 10.11.14 instance with mysql-connector-python 9.7.0 and Python 3.12.14. They verify a discounted purchase, stock deduction, payment confirmation and monthly report, plus rejection of insufficient stock, duplicate-item overselling, negative quantities and empty purchases. A MySQL 8 service runs these tests in CI. The Tk 9.0 GUI was launched against the isolated database in a virtual X display and closed automatically. Deprecated variable traces were migrated to trace_add for compatibility. Not every interactive workflow is verified. This remains a course project, not a production clinic system.

For integration checks, point DB_* to a **dedicated disposable test database**, set SMARTCLINIC_TEST_DATABASE to the same database name, and run:

```bash
python -m unittest discover -s tests -v
```

The test gate refuses a database whose name was not explicitly acknowledged. Test-created rows use fictional values and are cleaned up; do not run this on real operational data.

A tracked schema, integration tests, positive-quantity validation, duplicate aggregation and ordered product row locks are implemented. Remaining work includes full concurrent-worker tests, consistent decimal calculations and automated desktop interactions. Patient care, authentication and a clinical records system are outside the current implementation.

## License

[MIT](LICENSE).

## GUI transaction regression

`xvfb-run -a python -m unittest discover -s tests -v` runs the two database integration tests and one real Tk GUI flow against a dedicated database. The GUI test navigates all five pages, edits a fictional client/seller/product through form buttons, adds a cart item, finalizes a discounted purchase, checks persisted stock/payment/items and refreshes the purchase/dashboard screens. Confirmation dialogs are accepted by the test; errors fail it.

Verified locally with MariaDB 10.11.14, mysql-connector-python 9.7.0, Python 3.12.14 and Tk 9. MySQL 8.4 plus Xvfb is covered by CI. This is programmatic form/event-loop coverage, not a complete manual usability assessment or a concurrency stress test. Display-less local runs skip the GUI case explicitly.
