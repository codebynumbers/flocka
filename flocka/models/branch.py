import re
import subprocess
from datetime import datetime

from flask import current_app
from flask import render_template
from flask import request

from db import db, ActiveModel


class Branch(ActiveModel, db.Model):
    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    port = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String)
    created = db.Column(db.DateTime)
    container_id = db.Column(db.String(12))

    user = db.relationship("User", backref="branches")

    BASE_PORT = 8000
    END_PORT = 9000

    def run_container(self):
        if self.status != 'Running':
            self.port = self.get_available_port()
            self.created = datetime.utcnow()
            # the following need adequate permission
            self.start_container()
            if self.status == 'Running':
                self.add_vhost()
                self.reload_nginx()
            self.save()

    @classmethod
    def get_available_port(cls):
        used = {b.port for b in Branch.query.filter_by(status='Running').order_by(Branch.port).all()}
        for i in range(cls.BASE_PORT, cls.END_PORT):
            if i not in used:
                return i

    def add_vhost(self):
        template = self.get_vhost_template()
        with open("{}/{}.conf".format(current_app.config['NGINX_SITES_PATH'], self.name), "wb") as fh:
            fh.write(template)

    def get_vhost_template(self):
        context = dict(
            branch=self.name,
            hostname=request.host,
            port=self.port
        )
        return render_template('vhost/branch.conf.j2', **context)

    def start_container(self):
        if not self.port:
            self.port = self.get_available_port()
        cmd = ['docker', 'run', '-d', '-p', '{}:{}'.format(
            self.port, 5000), current_app.config['CONTAINER_NAME'], self.name]
        container_id = subprocess.check_output(cmd)
        if container_id:
            self.container_id = container_id[:12]
            self.status = self.check_status(self.container_id)

    def stop_container(self):
        cmd = ['docker', 'stop', self.container_id]
        container_id = subprocess.check_output(cmd)
        if container_id:
            self.container_id = container_id[:12]
            self.status = self.check_status(self.container_id)
            self.port = None

    def rm_container(self):
        cmd = ['docker', 'rm', self.container_id]
        subprocess.check_output(cmd)

    @staticmethod
    def reload_nginx():
        subprocess.call(current_app.config['NGINX_RELOAD_CMD'].split(' '))

    @staticmethod
    def is_container_running(container_id):
        return container_id and container_id in subprocess.check_output(['docker', 'ps'])

    @staticmethod
    def check_status(container_id):
        if Branch.is_container_running(container_id):
            status = 'Running'
        else:
            status = 'Stopped'
        return status