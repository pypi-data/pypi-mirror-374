from flask import session
from indico.core import signals
from indico.core.db import db
from indico.core.plugins import IndicoPlugin
from indico.modules.events.registration.controllers import RegistrationFormMixin
from indico.modules.events.registration.forms import RegistrationFormEditForm, _check_if_payment_required
from indico.modules.events.registration.models.forms import RegistrationForm
from indico.modules.events.registration.models.registrations import Registration
from indico_patcher import patch
from wtforms.fields import DecimalField
from wtforms.validators import Optional, NumberRange
from wtforms.widgets import NumberInput

from indico_price_adjustments import _


@patch(RegistrationFormEditForm)
class _RegistrationFormEditFormMixin:
    _price_fields = ('currency', 'base_price', 'extra_fee_for_guests')
    _special_fields = RegistrationFormEditForm._special_fields + _price_fields
    extra_fee_for_guests = DecimalField(_('Extra fee for guests'),
                                        [NumberRange(min=-999999999.99, max=999999999.99), Optional(),
                                         _check_if_payment_required],
                                        filters=[lambda x: x if x is not None else 0],
                                        widget=NumberInput(step='0.01'),
                                        description=_(
                                            'An extra fee guests(non-logged-in users) have to pay when registering, negative amounts supported.'))


@patch(RegistrationForm)
class _RegistrationFormMixin:
    extra_fee_for_guests = db.Column(
        db.Numeric(11, 2),  # max. 999999999.99
        nullable=False,
        default=0
    )


@signals.event.registration_created.connect  # Add fee if not logged in when registering
def registration_create_receiver(sender: Registration, data, management, **kwargs):
    if session:
        if session.user:
            return
    rfm = RegistrationFormMixin()
    rfm._process_args()
    sender.price_adjustment = rfm.regform.extra_fee_for_guests
    sender.sync_state()
    db.session.flush()


@signals.event.registration_updated.connect  # Remove fee if logded in before payment
def registration_update_receiver(sender: Registration, data, management, **kwargs):
    if not session:
        return
    if not session.user:
        return
    sender.price_adjustment = 0
    sender.sync_state()
    db.session.flush()


class PriceAdjustmentsPlugin(IndicoPlugin):
    """Price Adjustments

    Provides registration price adjustment options for non-logged-in users.
    """
    configurable = False

    def init(self):
        super().init()
        # self.inject_bundle('main.css', WPManageRegistration)
