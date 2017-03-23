from flask import abort, flash
from flask_login import login_required, current_user
from flocka.models import Branch


class LoginRequiredMixin(object):
    decorators = [login_required]


class SetBranchMixin(object):
    branch = None

    def dispatch_request(self, *args, **kwargs):
        if 'branch_id' in kwargs:
            self.branch = Branch.query.get(kwargs['branch_id'])
        return super(SetBranchMixin, self).dispatch_request(*args, **kwargs)

    def get_context_data(self, **context):
        context = super(SetBranchMixin, self).get_context_data(**context)
        context['branch'] = self.branch
        return context


class BranchAccessMixin(SetBranchMixin, LoginRequiredMixin):

    def dispatch_request(self, *args, **kwargs):
        dispatch = super(BranchAccessMixin, self).dispatch_request(*args, **kwargs)
        if self.branch and not current_user == self.branch.user:
            flash("Access Denied", "danger")
            abort(401)
        return dispatch

