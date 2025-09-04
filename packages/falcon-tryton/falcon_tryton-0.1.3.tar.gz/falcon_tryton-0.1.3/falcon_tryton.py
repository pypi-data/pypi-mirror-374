# This file is part of falcon_tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from functools import wraps
import falcon

from trytond import __version__ as trytond_version
from trytond.config import config
from trytond.exceptions import UserError, UserWarning, ConcurrencyException
from werkzeug.exceptions import BadRequest
from werkzeug.routing import BaseConverter

trytond_version = tuple(map(int, trytond_version.split('.')))

__version__ = '0.1.3'
__all__ = ['Tryton', 'tryton_transaction']

class Settings:    
    extensions = {}    

options = Settings()

class Tryton(object):
    def __init__(self, app=None, config={}, configure_jinja=False):
        self.app = app
        self.config_tryton = config
        self.context_callback = None
        self.database_retry = None
        self._configure_jinja = configure_jinja
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        "Initialize an application for the use with this Tryton setup."
        database = self.config_tryton.setdefault('TRYTON_DATABASE', None)
        user = self.config_tryton.setdefault('TRYTON_USER', 0)
        configfile = self.config_tryton.setdefault('TRYTON_CONFIG', None)        
        
        config.update_etc(configfile)

        from trytond.pool import Pool
        from trytond.transaction import Transaction

        Pool.stop = classmethod(lambda cls, database_name: None)  # Freeze pool

        self.database_retry = config.getint('database', 'retry')
        self.pool = Pool(database)
        with Transaction().start(database, user, readonly=True):
            self.pool.init()
        options.extensions['Tryton'] = self
            
    def default_context(self, callback):
        "Set the callback for the default transaction context"
        self.context_callback = callback
        return callback

    @property
    def language(self):
        "Return a language instance for the current request"
        from trytond.transaction import Transaction
        Lang = self.pool.get('ir.lang')
        # Do not use Transaction.language as it fallbacks to default language
        language = Transaction().context.get('language')
        if not language and request:
            language = request.accept_languages.best_match(
                Lang.get_translatable_languages())
        return Lang.get(language)

    def format_date(self, value, lang=None, *args, **kwargs):
        from trytond.report import Report
        if lang is None:
            lang = self.language
        return Report.format_date(value, lang, *args, **kwargs)

    def format_number(self, value, lang=None, *args, **kwargs):
        from trytond.report import Report
        if lang is None:
            lang = self.language
        return Report.format_number(value, lang, *args, **kwargs)

    def format_currency(self, value, currency, lang=None, *args, **kwargs):
        from trytond.report import Report
        if lang is None:
            lang = self.language
        return Report.format_currency(value, lang, currency, *args, **kwargs)

    def format_timedelta(
            self, value, converter=None, lang=None, *args, **kwargs):
        from trytond.report import Report
        if not hasattr(Report, 'format_timedelta'):
            return str(value)
        if lang is None:
            lang = self.language
        return Report.format_timedelta(
            value, converter=converter, lang=lang, *args, **kwargs)    

    @staticmethod
    def transaction(readonly=None, user=None, context=None):
        """Decorator to run inside a Tryton transaction.
        The decorated method could be run multiple times in case of
        database operational error.

        If readonly is None then the transaction will be readonly except for
        PUT, POST, DELETE and PATCH request methods.

        If user is None then TRYTON_USER will be used.

        readonly, user and context can also be callable.
        """
        from trytond import backend
        from trytond.transaction import Transaction
        try:
            from trytond.transaction import TransactionError
        except ImportError:
            class TransactionError(Exception):
                pass
        try:
            DatabaseOperationalError = backend.DatabaseOperationalError
        except AttributeError:
            DatabaseOperationalError = backend.get('DatabaseOperationalError')

        def get_value(value):
            return value() if callable(value) else value
        
        def req_readonly(req):
            return not (req
                and req.method in ('PUT', 'POST', 'DELETE', 'PATCH'))
            
        def instanciate(value):
            if isinstance(value, _BaseProxy):
                return value()
            return value

        def decorator(func):
            @wraps(func)
            def wrapper(_self, _req, _resp, *args, **kwargs):
                tryton = options.extensions['Tryton']
                request = _req                
                database = tryton.config_tryton.get('TRYTON_DATABASE', None)
                if user is None:
                    transaction_user = tryton.config_tryton.get('TRYTON_USER', 0)                   
                    
                else:
                    transaction_user = get_value(user)

                if readonly is None:
                    is_readonly = req_readonly(_req)
                else:
                    is_readonly = get_value(readonly)

                transaction_context = {}
                if tryton.context_callback or context:
                    with Transaction().start(database, transaction_user,
                            readonly=True):
                        if tryton.context_callback:
                            transaction_context = tryton.context_callback()
                        transaction_context.update(get_value(context) or {})

                transaction_context.setdefault('_request', {}).update({
                        'remote_addr': request.remote_addr,
                        'http_host': request.env.get('HTTP_HOST'),
                        'scheme': request.scheme,
                        # 'is_secure': request.is_secure,
                        } if request else {})

                retry = tryton.database_retry
                count = 0
                transaction_extras = {}
                while True:
                    if count:
                        time.sleep(0.02 * count)
                    with Transaction().start(
                            database, transaction_user,
                            readonly=is_readonly,
                            context=transaction_context,
                            **transaction_extras) as transaction:
                        try:
                            result = func(_self, _req, _resp, *map(instanciate, args),
                                **dict((n, instanciate(v))
                                    for n, v in kwargs.items()))
                        except TransactionError as e:
                            transaction.rollback()
                            transaction.tasks.clear()
                            e.fix(transaction_extras)
                            continue
                        except DatabaseOperationalError:
                            if count < retry and not transaction.readonly:
                                transaction.rollback()
                                transaction.tasks.clear()
                                count += 1
                                continue
                            raise
                        except (
                                UserError,
                                UserWarning,
                                ConcurrencyException) as e:
                            raise BadRequest(e.message)
                    from trytond.worker import run_task
                    while transaction.tasks:
                        task_id = transaction.tasks.pop()
                        run_task(tryton.pool, task_id)
                    return result
            return wrapper
        return decorator
    
tryton_transaction = Tryton.transaction


class _BaseProxy(object):
    pass


class _RecordsProxy(_BaseProxy):
    def __init__(self, model, ids):
        self.model = model
        self.ids = list(ids)

    def __iter__(self):
        return iter(self.ids)

    def __call__(self):
        tryton = options.extensions['Tryton']
        Model = tryton.pool.get(self.model)
        return Model.browse(self.ids)


class _RecordProxy(_RecordsProxy):
    def __init__(self, model, id):
        super(_RecordProxy, self).__init__(model, [id])

    def __int__(self):
        return self.ids[0]

    def __call__(self):
        return super(_RecordProxy, self).__call__()[0]


class RecordConverter(BaseConverter):
    """This converter accepts record id of model::

        Rule('/page/<record("res.user"):user>')"""
    regex = r'\d+'

    def __init__(self, map, model):
        super(RecordConverter, self).__init__(map)
        self.model = model

    def to_python(self, value):
        return _RecordProxy(self.model, int(value))

    def to_url(self, value):
        return str(int(value))


class RecordsConverter(BaseConverter):
    """This converter accepts record ids of model::

        Rule('/page/<records("res.user"):users>')"""
    regex = r'\d+(,\d+)*'

    def __init__(self, map, model):
        super(RecordsConverter, self).__init__(map)
        self.model = model

    def to_python(self, value):
        return _RecordsProxy(self.model, map(int, value.split(',')))

    def to_url(self, value):
        return ','.join(map(str, map(int, value)))
