from fifty_flask.views.generic import FormView, url_rule, RedirectView, GenericView, TemplateView
from flask import Blueprint, url_for, flash
from flask import request
from flask_login import current_user

from fifty_tables import NumericColumn, LinkColumn, FiftyTableColumn
from fifty_tables.views import SQLAlchemyTableView
from slugify import slugify

from flocka.controllers.mixins import BranchAccessMixin, LoginRequiredMixin
from flocka.forms.branch import BranchForm
from flocka.models.branch import Branch

branched_bp = Blueprint('branches', __name__, url_prefix='/branches')


@url_rule(branched_bp, ['/<branch_id>/edit/', '/edit/'], 'edit')
class BranchEditView(BranchAccessMixin, FormView):

    template_name = "branch_edit.html"
    form_cls = BranchForm
    redirect_endpoint = '.list'

    def _get_branch(self):
        """ Get the model to save.
            Could be new in case of create, or existing.
        """
        if not self.branch:
            self.branch = Branch()
        return self.branch

    def get_form_obj(self):
        return self.branch

    def form_valid(self, form, **context):
        branch = Branch.query.filter_by(name=form.name.data).first() or self._get_branch()
        form.populate_obj(branch)
        branch.user = current_user
        branch.save()
        if not Branch.is_container_running(branch.container_id):
            branch.run_container()
        self.branch = branch
        flash("Branch saved", "success")
        return super(BranchEditView, self).form_valid(form, **context)

    def form_invalid(self, form, **context):
        flash("Error saving branch", "danger")
        return super(BranchEditView, self).form_invalid(form, **context)


@url_rule(branched_bp, '/', 'list')
class BranchListView(LoginRequiredMixin, SQLAlchemyTableView):
    template_name = 'branch_list.html'
    default_sort = 'id'
    default_sort_direction = 'asc'

    def get_table_columns(self, params=None, **context):
        class SelfLinkColumn(LinkColumn):
            def get_link_text(self, row):
                return self.get_url(row)

            def get_link_attributes(self, row, **kwargs):
                return {'target': '_blank'}

        class RunningColumn(FiftyTableColumn):
            def get_value(self, row, **kwargs):
                return Branch.check_status(row['container_id'])

        return [
            NumericColumn(name='id', label='ID', int_format='{:}'),
            FiftyTableColumn(name='container_id', label="Container ID"),
            LinkColumn(name='name', label="Name",
                       endpoint='.edit', url_params={'branch_id': 'id'}),
            NumericColumn(name='port', label='Port', int_format='{:}'),
            SelfLinkColumn('url', label='Url',
                       url="http://{subdomain}." + request.host,
                       url_params={'subdomain': 'slug'}),
            RunningColumn(name='status'),
            FiftyTableColumn(name='actions', label='Actions', sortable=False, cell_template='tables/cells/actions.html')
        ]

    def process_rows(self, rows, params=None, **context):
        for row in rows:
            row['slug'] = slugify(row['name'])
        return rows

    def get_query(self, params, **context):
        return Branch.query.filter_by(user=current_user)


class BranchActionView(BranchAccessMixin, RedirectView):

    redirect_endpoint = 'branches.list'

    def get_context_data(self, **context):
        return {}


@url_rule(branched_bp, '/<branch_id>/start/', 'start')
class BranchStartView(BranchActionView):

    def get(self, *args, **kwargs):
        Branch.start_container(self.branch)
        return super(BranchStartView, self).get(*args, **kwargs)


@url_rule(branched_bp, '/<branch_id>/stop/', 'stop')
class BranchStopView(BranchActionView):

    def get(self, *args, **kwargs):
        Branch.stop_container(self.branch)
        Branch.rm_container(self.branch)
        return super(BranchStopView, self).get(*args, **kwargs)


@url_rule(branched_bp, '/<branch_id>/delete/', 'delete')
class BranchDeleteView(BranchActionView):

    def get(self, *args, **kwargs):
        try:
            Branch.stop_container(self.branch)
            Branch.rm_container(self.branch)
        except:
            pass
        self.branch.delete()
        return super(BranchDeleteView, self).get(*args, **kwargs)


@url_rule(branched_bp, ['/<branch_id>/logs/'], 'logs')
class BranchLogView(BranchAccessMixin, TemplateView):

    template_name = "branch_logs.html"

    def get_context_data(self, **context):
        context = super(BranchLogView, self).get_context_data(**context)
        context['logs'] = self.branch.get_logs(request.values.get('lines'))
        return context