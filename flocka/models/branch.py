from datetime import datetime
import subprocess
from random import randint

from flask import current_app
from flask import render_template
from flask import request
from slugify import slugify

from db import db, ActiveModel
from flocka.services import docker_client


class Branch(ActiveModel, db.Model):
    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    port = db.Column(db.Integer, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20))
    created = db.Column(db.DateTime)
    container_id = db.Column(db.String(12))

    user = db.relationship("User", backref="branches")

    BASE_PORT = 8000
    END_PORT = 9000
    DEFAULT_NUM_LINES = 1000

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
        port = randint(cls.BASE_PORT, cls.END_PORT)
        while port in used:
            port = randint(cls.BASE_PORT, cls.END_PORT)
        return port

    def add_vhost(self):
        template = self.get_vhost_template()
        with open("{}/{}.conf".format(
                current_app.config['NGINX_SITES_PATH'], slugify(self.name)), "wb") as fh:
            fh.write(template)

    def get_vhost_template(self):
        context = dict(
            branch=slugify(self.name),
            hostname=request.host.split(':')[0],
            port=self.port,
            app_path=current_app.root_path
        )
        return render_template('vhost/branch.conf.j2', **context)

    def start_container(self):
        if not self.port:
            self.port = self.get_available_port()
        cmd = [
            'docker', 'run', '-d',
            '-p', '{}:{}'.format(self.port, 5000),
            current_app.config['CONTAINER_NAME'],
            self.name,
            "{}.{}".format(slugify(self.name), request.host.split(':')[0])
        ]
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

    def get_logs(self, num_lines, reverse=False):
        try:
            num_lines = int(num_lines)
        except:
            num_lines = self.DEFAULT_NUM_LINES

        if self.is_container_running(self.container_id):
            logs = docker_client.containers.get(self.container_id).logs(tail=num_lines).splitlines()
            if reverse:
                logs = reversed(logs)
            return "\n".join(logs)

    @staticmethod
    def get_log_stream(container_id):
        return docker_client.containers.get(container_id).logs(stream=True)
