"""
This file defines the database models
"""
import datetime

from .common import db, Field, T, auth
from pydal.validators import *


########################################
db.define_table('t_org',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_code', type='string',
          label=T('Code')),
    auth.signature,
    format='%(f_name)s')

#db._common_fields.append(Field('f_tenantid', type='integer', default=None))

########################################
db.define_table('t_org_user',
    Field('f_userid', db.auth_user, default=auth.user_id),
    Field('f_org', type='reference t_org',
          label=T('Organisation')),
    auth.signature,
    format='%(f_name)s')

########################################
db.define_table('t_device',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_code', type='string',
          label=T('Code')),
    Field('f_type', type='string',
          label=T('Type')),
    Field('f_org', type='reference t_org',
          label=T('Organisation')),
    auth.signature,
    format='%(f_name)s')

########################################
db.define_table('t_equipment',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_desc', type='string',
          label=T('Desc')),
    Field('f_org', type='reference t_org',
          label=T('Organisation')),
    auth.signature,
    format='%(f_name)s')

########################################
db.define_table('t_sensor',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_type', type='string',
          label=T('Type')),
    Field('f_units', type='string',
          label=T('Units')),
    Field('f_code', type='string',
          label=T('Code')),
    Field('f_equipment', type='reference t_equipment',
          label=T('Equipment')),
    Field('f_device', type='reference t_device',
          label=T('Device')),
    auth.signature,
    format='%(f_name)s')

########################################
db.define_table('t_samples',
    Field('f_sensor', type='reference t_sensor',
          label=T('Sensor')),
    Field('f_value', type='double',
          label=T('Value')),
    Field('f_timestamp', type='integer',
          label=T('Timestamp')),
    auth.signature,
    format='%(f_sensor)s')

########################################
db.define_table('t_product',
    Field('f_name', type='string',
          label=T('Name')),
    Field('f_desc', type='string',
          label=T('Desc')),
    Field('f_type', type='string',
          label=T('Type')),
    Field('f_org', type='reference t_org',
          label=T('Organisation')),
    auth.signature,
    format='%(f_name)s')

########################################
db.define_table('t_batch',
    Field('f_product', type='reference t_product',
          label=T('Product')),
    Field('f_equipment', type='reference t_equipment',
          label=T('Equipment')),
    Field('f_start', type='datetime',
          label=T('Start')),
    Field('f_end', type='datetime',
          label=T('End')),
    Field('f_serial', type='string',
          label=T('Serial')),
    auth.signature,
    format='%(f_product)s')

# simple table example
db.define_table(
    "person",
    Field("name", requires=IS_NOT_IN_DB(db, "person.name"), label=T("name")),
    Field("job", requires=IS_NOT_EMPTY(), label=T("job")),
    Field("resume", "json", label=T('resume'), default=[]),
    format="%(name)s",
)

# simple reference example
db.define_table(
    "superhero",
    Field("name"),
    Field("real_identity", "reference person"),
    format="%(name)s",
)

db.define_table("superpower", Field("description"), format="%(description)s")

# many to many example
db.define_table(
    "tag",
    Field("superhero", "reference superhero"),
    Field("superpower", "reference superpower"),
    Field("strength", "integer"),
)

if not db(db.person).count():
    db.person.insert(
        name="Clark Kent",
        job="Journalist",
        resume=[
            {
                "start_date": "2019-12-20",
                "end_date": "2020-01-20",
                "company": "Save The World Srl",
            },
            {
                "start_date": "2020-02-01",
                "end_date": "2020-03-15",
                "company": "SuperHeroes Services Srl",
            },
        ],
    )
    db.person.insert(name="Peter Park", job="Photographer")
    db.person.insert(name="Bruce Wayne", job="CEO")
    db.superhero.insert(name="Superman", real_identity=1)
    db.superhero.insert(name="Spiderman", real_identity=2)
    db.superhero.insert(name="Batman", real_identity=3)
    db.superpower.insert(description="Flight")
    db.superpower.insert(description="Strength")
    db.superpower.insert(description="Speed")
    db.superpower.insert(description="Durability")
    db.tag.insert(superhero=1, superpower=1, strength=100)
    db.tag.insert(superhero=1, superpower=2, strength=100)
    db.tag.insert(superhero=1, superpower=3, strength=100)
    db.tag.insert(superhero=1, superpower=4, strength=100)
    db.tag.insert(superhero=2, superpower=2, strength=50)
    db.tag.insert(superhero=2, superpower=3, strength=75)
    db.tag.insert(superhero=2, superpower=4, strength=10)
    db.tag.insert(superhero=3, superpower=2, strength=80)
    db.tag.insert(superhero=3, superpower=3, strength=20)
    db.tag.insert(superhero=3, superpower=4, strength=70)

# Used for examples of forms.
def get_user_email():
    return None if auth.current_user is None else auth.current_user.get("email")

def get_time():
    return datetime.datetime.utcnow()

db.define_table(
    'product',
    Field('product_name'),
    Field('product_quantity', 'integer',
          requires=IS_INT_IN_RANGE(0, None),
          default=0),
    Field('product_cost', 'float',
          requires=IS_FLOAT_IN_RANGE(0, None), default=0.),
    Field('mail_order', 'boolean'),
    Field('created_by', default=get_user_email),
    Field('creation_date', 'datetime', default=get_time)
)

# We do not want these fields to appear in forms by default.
db.product.id.readable = False
db.product.created_by.readable = False
db.product.creation_date.readable = False



db.commit()
