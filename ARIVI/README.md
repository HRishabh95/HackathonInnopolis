# Unidoctor-api

Run

```bash
python3 manage.py runserver 3001
```

Run tests via Behave-Django

```bash
# on its own
python3 manage.py behave --keepdb ./features

# with Allure formatter to generate Allure reports
python3 manage.py behave --keepdb -f allure_behave.formatter:AllureFormatter -o allure_results ./features
```

Serve Allure reports

```
allure serve allure_results
```

Coverage:

coverage erase

coverage run --branch --source=clinics,diagnosis,message,reports,sales,treatment_courses manage.py runserver 3001
coverage run --branch --source=clinics,diagnosis,message,reports,sales,treatment_courses manage.py behave --keepdb -f allure_behave.formatter:AllureFormatter -o allure_results ./features
coverage xml -i

