
from flask import render_template, Blueprint, url_for, flash, redirect, request, abort
from OraApp import db, bcrypt
from OraApp.forms import Admin_Applicant_Add, Admin_Applicant_Update, User_Login, Admin_Update, Admin_Add, Admin_Edit
from OraApp.models import Admin, User, Job, Employer, Applicant
from OraApp.utils import user_role_required, save_file, remove_file
from flask_login import login_user, current_user


admin = Blueprint('admin', __name__)

# @admin.route("/admin")
@admin.route("/admin/dashboard/")
@user_role_required('admin')
def admin_account():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    jobs = len(Job.query.all())
    employers = len(Employer.query.all())
    applicants = len(Applicant.query.all())

    dash = {'jobs': jobs, 'employers': employers, 'applicants': applicants}
    return render_template("admin/dashboard.html", title="Admin | Dashboard", user=user, dash=dash )

@admin.route("/admin/job-categories/")
@user_role_required('admin')
def admin_job_categories():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    return render_template("admin/dashboard.html", title="Admin | Job Categories", user=user)

@admin.route("/admin/jobs-list/")
@user_role_required('admin')
def admin_jobs():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    return render_template("admin/dashboard.html", title="Admin | Lists of Jobs", user=user)

@admin.route("/admin/companies/")
@user_role_required('admin')
def admin_companies():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    return render_template("admin/dashboard.html", title="Admin | Manage Companies", user=user)



@admin.route("/admin/applicants/")
@user_role_required('admin')
def admin_applicants():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    users = Applicant.query.all()
    return render_template("admin/applicants.html", title="Admin | Manage Applicants", user=user, applicants=users)

@admin.route("/admin/applicants/new-applicant/", methods=['GET', 'POST'])
@user_role_required('admin')
def admin_applicant_add():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    form = Admin_Applicant_Add()
    if form.validate_on_submit():
        resume = save_file('applicant/resume/', form.resume.data)
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(email=form.email.data, user_role='applicant', password=pw_hash)
        db.session.add(user)
        
        applicant = Applicant(f_name=form.f_name.data.strip().capitalize(), l_name=form.l_name.data.strip().capitalize(), phone=form.phone.data, resume=resume, applicant=user)
        db.session.add(applicant)
        db.session.commit()
        
        flash(f'New Applicant Added Successfully!', 'success')
        return redirect(url_for('.admin_applicants'))
    return render_template("admin/new_applicants.html", title="Admin | Add Applicants", user=user, form=form)

@admin.route("/admin/<int:applicant_id>/remove-applicant/", methods=['POST'])
@user_role_required('admin')
def admin_applicant_remove(applicant_id):
    user = Applicant.query.get_or_404(applicant_id)

    db.session.delete(user)
    db.session.delete(user.applicant)
    db.session.commit()

    if user.resume:
        file = f'applicant/resume/{str(user.resume)}'
        try:
            remove_file(file)
        except FileNotFoundError:
            flash(f'File not Found!', category='danger')

    if user.image and user.image != "anony.png":
        file = f'applicant/image/{str(user.image)}'
        try:
            remove_file(file)
        except FileNotFoundError:
            flash(f'File not Found!', category='danger')
            

    flash(f'Applicant Removed Successfully!', 'success')
    return redirect(url_for('.admin_applicants'))

@admin.route("/admin/applicants/<int:applicant_id>/update-applicant/", methods=['GET', 'POST'])
@user_role_required('admin')
def admin_applicant_update(applicant_id):
    user = Admin.query.filter_by(user_id=current_user.id).first()
    updated = Applicant.query.get_or_404(applicant_id)
    form = Admin_Applicant_Update()

    form.id.data = int(applicant_id)
    if form.validate_on_submit():
        updated.f_name = form.f_name.data.strip().capitalize()
        updated.l_name = form.l_name.data.strip().capitalize()
        updated.applicant.email = form.email.data
        updated.phone = form.phone.data 


        # if form.resume.data:
            # doc = save_file('applicant/resume/', form.resume.data)
            # if doc:
            #     updated.resume = doc

        db.session.commit()
        flash(f'Applicant Updated Successfully. {updated.resume}', 'success')
        return redirect(url_for('.admin_applicants'))
        
    form.f_name.data = updated.f_name 
    form.l_name.data = updated.l_name
    form.email.data = updated.applicant.email
    form.phone.data = updated.phone
    
    return render_template("admin/update_applicants.html", title="Admin | Update Applicants", form=form, user=user, updated=updated)



@admin.route("/admin/notifications/")
@user_role_required('admin')
def admin_notifications():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    return render_template("admin/dashboard.html", title="Admin | Notifications")

@admin.route("/admin/settings/", methods=['GET', 'POST'])
@user_role_required('admin')
def admin_settings():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    admins = Admin.query.all()
    form = Admin_Update()

    if form.validate_on_submit():
        user.name = form.name.data.strip().capitalize()
        current_user.email = form.email.data 
        user.phone = form.phone.data 
        if form.image.data:
            img = save_file('admin/image/', form.image.data)
            if img:
                if user.image != 'anony.png':
                    file = f'admin/image/{str(user.image)}'
                    remove_file(file)
                user.image = img

        db.session.commit()
        flash(f'Information Updated Successfully.', 'success')
        return redirect(url_for('.admin_settings'))

    form.name.data = user.name
    form.email.data = current_user.email
    form.phone.data = user.phone
    return render_template("admin/settings.html", title="Admin | Settings", form=form, user=user, admins=admins)

@admin.route("/admin/settings/add-admin/", methods=['GET', 'POST'])
@user_role_required('admin')
def admin_add():
    user = Admin.query.filter_by(user_id=current_user.id).first()
    form = Admin_Add()
    if form.validate_on_submit():
        pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(email=form.email.data, user_role='admin', password=pw_hash)
        db.session.add(user)
        
        admin = Admin(name=form.name.data.strip().capitalize(), phone=form.phone.data, admin=user)
        db.session.add(admin)
        db.session.commit()
        
        flash(f'New Admin Added Successfully!', 'success')
        return redirect(url_for('.admin_settings'))
    
    return render_template("admin/new.html", title="Admin | Settings", form=form, user=user)

@admin.route("/admin/<int:admin_id>/update-admin/", methods=['GET', 'POST'])
@user_role_required('admin')
def admin_update(admin_id):
    user = Admin.query.filter_by(user_id=current_user.id).first()
    updated = Admin.query.get_or_404(admin_id)
    form = Admin_Edit()
    form.id.data = int(admin_id)
    if form.validate_on_submit():
        updated.name = form.name.data.strip().capitalize()
        updated.admin.email = form.email.data
        updated.phone = form.phone.data 

        db.session.commit()
        
        flash(f'Admin Updated Successfully!', 'success')
        return redirect(url_for('.admin_settings'))
        
    form.name.data = updated.name 
    form.email.data = updated.admin.email
    form.phone.data = updated.phone 
    return render_template("admin/update.html", title="Admin | Settings", form=form, user=user, updated=updated)
  

@admin.route("/admin/<int:admin_id>/remove", methods=['POST'])
@user_role_required('admin')
def admin_remove(admin_id):
    user = Admin.query.get_or_404(admin_id)

    db.session.delete(user)
    db.session.delete(user.admin)
    db.session.commit()

    if user.image and user.image != "anony.png":
        file = f'admin/image/{str(user.image)}'
        try:
            remove_file(file)
        except FileNotFoundError:
            flash(f'File not Found!', category='danger')

    flash(f'Admin Removed Successfully!', 'success')
    return redirect(url_for('.admin_settings'))


@admin.route("/admin/<int:admin_id>/delete-image", methods=['POST'])
@user_role_required('admin')
def delete_image(admin_id):
    user = Admin.query.get_or_404(admin_id)
    if not user.admin == current_user:
        abort(403)

    if user.image and user.image != "anony.png":
        file = f'admin/image/{str(user.image)}'
        try:
            remove_file(file)
            user.image = 'anony.png'
            db.session.commit()
            flash(f'Image Removed Successfully!', category='success')
        except FileNotFoundError:
            user.image = 'anony.png'
            db.session.commit()
            flash(f'File not Found!', category='danger')
    
    return redirect(url_for('.admin_settings'))


@admin.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.user_role == 'admin':
        return redirect(url_for('.admin_account'))
    form = User_Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.user_role == 'admin' and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Admin Login successs.', 'success')

            return redirect(request.args.get('next') or url_for('.admin_account'))
        else:
            flash(f'Invalid Email or Password! Please Try Again.', 'danger')
    return render_template("admin/login.html", title="OraJobs | Admin Login", form=form)