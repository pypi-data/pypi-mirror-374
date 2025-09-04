import pytest

from caproto import AlarmSeverity, AlarmStatus, ChannelType
from caproto.sync.client import read, write
from caproto.threading.pyepics_compat import get_pv

from .test_threading_client import context as _context
from .test_threading_client import shared_broadcaster as _sb

context = _context
shared_broadcaster = _sb

field_map = {
    'upper_ctrl_limit': 'HOPR',
    'lower_ctrl_limit': 'LOPR',

    'upper_alarm_limit': 'HIHI',
    'lower_alarm_limit': 'LOLO',

    'upper_warning_limit': 'HIGH',
    'lower_warning_limit': 'LOW',
}


def test_limit_fields_and_description(request, prefix, context, records_ioc):
    pv = records_ioc.pvs["C"]
    PV = get_pv(pv, context=context)

    def check_fields():
        for k, v in PV.get_ctrlvars().items():
            if k in field_map:
                fv, = read(f'{pv}.{field_map[k]}').data
                assert v == fv

    check_fields()
    for v in field_map.values():
        work_pv = f'{pv}.{v}'
        write(work_pv, 2 * read(work_pv).data)
    check_fields()

    def string_read(pv):
        return b''.join(read(pv, data_type=ChannelType.STRING).data)

    assert string_read(f'{pv}.DESC') == b'The C pvproperty'
    write(f'{pv}.DESC', 'a new description', notify=True)
    assert string_read(f'{pv}.DESC') == b'a new description'


@pytest.mark.parametrize('sevr_target', ['LLSV', 'LSV', 'HSV', 'HHSV'])
@pytest.mark.parametrize('sevr_value', AlarmSeverity)
def test_alarms(request, prefix, sevr_target, sevr_value, context, records_ioc):
    pv = records_ioc.pvs["C"]
    PV = get_pv(pv, context=context)
    sevr_target_pv = get_pv(f'{pv}.{sevr_target}', context=context)
    sevr_target_pv.put(sevr_value, wait=True)

    def get_severity(postfix):
        if postfix == sevr_target:
            postfix_pv = sevr_target_pv
        else:
            postfix_pv = get_pv(f'{pv}.{postfix}', context=context)

        return postfix_pv.get(
            as_string=False,
            use_monitor=False,
        )

    assert get_severity(sevr_target) == sevr_value, "Specified severity not set"

    checks = (
        ('lower_ctrl_limit', 'lower_alarm_limit',
         AlarmStatus.LOLO, get_severity('LLSV')),
        ('lower_alarm_limit', 'lower_warning_limit',
         AlarmStatus.LOW, get_severity('LSV')),
        ('lower_warning_limit', 'upper_warning_limit',
         AlarmStatus.NO_ALARM, AlarmSeverity.NO_ALARM),
        ('upper_warning_limit', 'upper_alarm_limit',
         AlarmStatus.HIGH, get_severity('HSV')),
        ('upper_alarm_limit', 'upper_ctrl_limit',
         AlarmStatus.HIHI, get_severity('HHSV')),

    )

    for minv, maxv, a_status, a_sevr in checks:
        ctrl_vars = PV.get_ctrlvars()
        v = (ctrl_vars[minv] + ctrl_vars[maxv]) / 2
        PV.put(v, wait=True)

        ctrl_vars = PV.get_ctrlvars()
        assert ctrl_vars['status'] == a_status
        assert ctrl_vars['severity'] == a_sevr
