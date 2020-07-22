"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
import os
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from py4web import action, request, abort, redirect, URL, Field, DAL
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.publisher import Publisher, ALLOW_ALL_POLICY
from pydal.validators import IS_NOT_EMPTY, IS_INT_IN_RANGE, IS_IN_SET, IS_IN_DB
from yatl.helpers import A, SPAN, DIV, INPUT, H1, HTML, BODY

# exposes services necessary to access the db.thing via ajax
publisher = Publisher(db, policy=ALLOW_ALL_POLICY)


@action("index")
@action.uses(auth, "index.html")
def index():
    return {}


@action("simple_page")
def simple_page():
    return "ok"


@action("error")
def error():
    1 / 0

@action("session/counter")
@action.uses(session)
def session_counter():
    session['counter'] = session.get('counter', 0) + 1
    return str(session.get('counter'))

@action("session/clear")
@action.uses(session)
def session_clear():
    session.clear()
    return 'done'


# exposed as /examples/create_form or /examples/update_form/<id>
@action("create_form", method=["GET", "POST"])
@action("update_form/<id>", method=["GET", "POST"])
@action.uses("form.html", db, session, T, auth)
def example_form(id=None):
    form = Form(db.person, id, deletable=False, formstyle=FormStyleBulma)
    rows = db(db.person).select()
    return dict(form=form, rows=rows)


# exposed as /examples/custom_form
@action("custom_form", method=["GET", "POST"])
@action.uses("custom_form.html", db, session, T, auth)
def custom_form(id=None):
    form = Form(db.person, id, deletable=False, formstyle=FormStyleBulma)
    rows = db(db.person).select()
    return dict(form=form, rows=rows)


# exposed as /examples/grid
@action("product")
@action.uses(auth.user, T, db,"grid.html")
def example_grid():
    title = 'Products'
    subtitle = 'What are we making?'
    return dict(title=title, subtitle=subtitle, grid=publisher.grid(db.t_product))

# exposed as /examples/grid
@action("equipment")
@action.uses(auth.user, T, db, "grid.html")
def example_grid():
    title = 'Equipment'
    subtitle = 'What we use to make stuff...'
    return dict(title=title, subtitle=subtitle, grid=publisher.grid(db.t_equipment))

@action("device")
@action.uses(auth.user, T, db,"grid.html")
def example_grid():
    title = 'Devices'
    subtitle = 'Edge devices that transmit data.'
    return dict(title=title, subtitle=subtitle, grid=publisher.grid(db.t_device))

@action("hello")
@action.uses(T)
def hello():
    return str(T("Hello World"))


@action("count")
@action("count/<number:int>")
@action.uses(T)
def count(number=1):
    message = T("Cat").format(n=number)
    link = A(T("more"), _href=URL("count/%s" % (number + 1)))
    return HTML(BODY(H1(message, " ", link))).xml()


@action("forms", method=["GET", "POST"])
@action.uses(auth.user, "forms.html", session, db, T)
def example_multiple_forms():
    name = Field("name", requires=IS_NOT_EMPTY())
    forms = [
        Form(
            [Field("name", requires=IS_NOT_EMPTY())],
            form_name="1",
            formstyle=FormStyleBulma,
        ),
        Form(
            [Field("name", requires=IS_NOT_EMPTY())],
            form_name="2",
            keep_values=True,
            formstyle=FormStyleBulma,
        ),
        Form(
            [Field("name", requires=IS_NOT_EMPTY()), Field("age", "integer")],
            form_name="3",
            formstyle=FormStyleBulma,
        ),
        Form(
            [Field("name", requires=IS_NOT_EMPTY()), Field("insane", "boolean")],
            form_name="4",
            formstyle=FormStyleBulma,
        ),
        Form(
            [
                Field("name", requires=IS_NOT_EMPTY()),
                Field("color", requires=IS_IN_SET(["red", "blue", "green"])),
            ],
            form_name="5",
            formstyle=FormStyleBulma,
        ),
        Form(
            [
                Field("name", requires=IS_NOT_EMPTY()),
                Field(
                    "favorite_hero", requires=IS_IN_DB(db, "person.id", "person.name")
                ),
            ],
            form_name="6",
            formstyle=FormStyleBulma,
        ),
    ]
    messages = []
    for form in forms:
        if form.accepted:
            messages.append("form %s accepted with: %s " % (form.form_name, form.vars))
        elif form.errors:
            messages.append("form %s has errors: %s " % (form.form_name, form.errors))
    return dict(forms=forms, messages=messages)


# exposed as /examples/showme
@action("helpers")
@action.uses("generic.html")
def example_helpers():
    return dict(a=H1("I am a title"), b=2, c=dict(d=3, e=4, x=INPUT(_name="test")))


# automatic actions


@unauthenticated.get()  # exposed as /hello_world
def hello_world():
    return dict()


@unauthenticated.get()  # exposed as /hello_world/<msg>
def hello_world(msg):
    return dict(msg=msg)


@unauthenticated.callback("click me")
def a_callback(msg):
    import logging

    logging.info(msg)


@unauthenticated.get()
def show_a_button():
    return dict(mybutton=a_callback.button("clickme")(msg="hello world"))

@authenticated()
@action('dashboard')
@action.uses(auth.user, T, db, 'dashboard.html')
def dashboard():
    title = 'Dashboard'
    subtitle = 'Where are we at?'
    #response.meta.author
    #response.meta.keywords
    #response.meta.description

    userid = auth.user_id

    batches = db().select(db.t_batch.ALL)
    #org_eq = db().select(db.t_equipment.ALL)
    org_eq=db((userid == db.t_org_user.f_userid) & (db.t_org.id == db.t_org_user.f_org)
              & (db.t_equipment.f_org == db.t_org.id)
              ).select(db.t_equipment.ALL)
    org_eq_ba = db((db.t_equipment.f_org == db.t_org.id)& (db.t_batch.f_equipment == db.t_equipment.id) & (db.t_batch.f_end == None)).select()
                   #& (db.t_org.id == auth.user.f_org)

    # org_eq_bas = org_eq_ba.select()
    # org_eq_batches = db(orgequipment.t_equipment.f_id == batches.f_equipment).select(ALL)
    products = db().select(db.t_product.ALL)
    # orgequipment = json.dumps(orgeq.as_list())
    # Convert to XML for DataTable

    return dict(title=title, subtitle=subtitle, org_eq_ba=org_eq_ba, org_eq=org_eq, products=products)


@authenticated()
def batch_new():
    #jsdict = request.get_vars
    jsdict = request.post_vars
    #eqid = jsdict['eqid']
    dt = datetime.strptime(jsdict['startdate'], '%Y-%m-%dT%H:%M')

    newbatch = db.t_batch.update_or_insert(f_product=jsdict['pr_id'], f_equipment=jsdict['eq_id'], f_start=dt)
    db.commit()
    redirect(URL('Qualitiv','default','dashboard'))

    """
    http://127.0.0.1:8000/a/c/f.html/x/y/z?p=1&q=2
    to function f in controller "c.py" in application a, and it stores the URL parameters in the request variable as follows:
    request.args = ['x', 'y', 'z']
    request.vars = {'p': 1, 'q': 2}
    """
    return locals()

from datetime import datetime
@unauthenticated()
def insert_data():
    getput = request.env.request_method
    jsdict = request.get_vars
    dev = -1
    value = -1
    timestamp = -1
    dt_object = None
    sensor = None
    #Strip out the data we need and push it into the samples.
    #Need to parse through the JSON to find AI01Avg and AI02Avg
    """{"AI01Avg": 290, "AI01Max": 291, "AI01Min": 288, "DeviceId": "RTK_000002", "Organisation": "PACSEEDS", "Site": "KUNUNURRA", "Type": "TEMP", "timestamp": 1594101598151}"""
    """{"AI02Avg": 291, "AI02Max": 291, "AI02Min": 291, "DeviceId": "RTK_000002", "Organisation": "PACSEEDS", "Site": "KUNUNURRA", "Type": "TEMP", "timestamp": 1594100998527}"""
    #RTK_000002
    #RTK_000002
    try:
        deviceid    = jsdict['DeviceId']
        devicetype  = jsdict['Type']

        devid = db.t_device.update_or_insert(db.t_device.f_code == deviceid, f_code = deviceid, f_type = devicetype, f_name = deviceid)
        db.commit()
        dev = db.t_device(db.t_device.f_code == deviceid)

        org         = jsdict['Organisation']
        site        = jsdict['Site']
        if devicetype == 'TEMP' or devicetype == 'WTANK':
            try:
                if 'AI01Avg' in jsdict and 'timestamp' in jsdict:
                    sensorcode = 'AI01Avg'

                    value     = jsdict[sensorcode]
                    timestamp   = jsdict['timestamp']
                    db.t_sensor.update_or_insert((db.t_sensor.f_code == sensorcode) & (db.t_sensor.f_device == dev.id), f_code = sensorcode, f_device = dev.id, f_name = str(dev.f_name) + '/' + str(sensorcode))
                    db.commit()
                    sensor = db.t_sensor((db.t_sensor.f_code == sensorcode) & (db.t_sensor.f_device == dev.id))
                    db.t_samples.update_or_insert((db.t_samples.f_sensor == sensor.id) & (db.t_samples.f_timestamp == timestamp) & (db.t_samples.f_value == value), f_sensor = sensor.id, f_value = value, f_timestamp = timestamp)
                    db.commit()
                if 'AI02Avg' in jsdict and 'timestamp' in jsdict:
                    sensorcode = 'AI02Avg'

                    value     = jsdict[sensorcode]
                    timestamp   = jsdict['timestamp']
                    db.t_sensor.update_or_insert((db.t_sensor.f_code == sensorcode) & (db.t_sensor.f_device == dev.id), f_code = sensorcode, f_device = dev.id, f_name = str(dev.f_name) + '/' + str(sensorcode))
                    db.commit()
                    sensor = db.t_sensor((db.t_sensor.f_code == sensorcode) & (db.t_sensor.f_device == dev.id))
                    db.t_samples.update_or_insert((db.t_samples.f_sensor == sensor.id) & (db.t_samples.f_timestamp == timestamp) & (db.t_samples.f_value == value), f_sensor = sensor.id, f_value = value, f_timestamp = timestamp)
                    db.commit()
            except:
                print("Expected JSON AI02Avg missing")
    except Exception as e:
        print("Expected JSON data missing " + str(e))
    return dict(jsdict=jsdict, dev=dev,deviceid=deviceid,value=value, sensor=sensor, timestamp=timestamp,devicetype=devicetype,dt_object=dt_object,devid=devid)
