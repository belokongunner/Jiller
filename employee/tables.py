import django_tables2 as tables
from django_tables2.utils import A
from .models import Employee


class EmployeeTable(tables.Table):
    id = tables.Column()
    get_full_name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')},\
                                      order_by=('last_name'), verbose_name='Name')
    email = tables.Column()
    date_joined = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    is_active = tables.BooleanColumn(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Employee
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id')
        fields = ['get_full_name', 'email', 'date_joined', 'is_active']

