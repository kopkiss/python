from django.db import models

# Create your models here.

class Get_db(models.Model):  #สร้างตาราง
    customer_id = models.IntegerField()
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)

class Get_db_oracle(models.Model):
    customer_id = models.CharField(max_length = 3)
    fullname = models.CharField(max_length = 200)
    email = models.EmailField()
    country_code = models.CharField(max_length = 2)
    budget = models.IntegerField()
    used = models.FloatField()

class Prpm_v_grt_project_eis(models.Model):
    psu_project_id = models.CharField(max_length = 5)
    submit_name_surname_th = models.CharField(max_length = 500)
    pj_status_th = models.CharField(max_length = 500)
    fund_budget_year = models.IntegerField()
    fund_source_th = models.CharField(max_length = 500)
    fund_type_th = models.CharField(max_length = 300)
    faculty_owner = models.CharField(max_length = 300)
    camp_owner = models.CharField(max_length = 300)
    sum_budget_plan = models.DecimalField(max_digits=19, decimal_places=10)


class PRPM_v_grt_pj_team_eis(models.Model):
    staff_id = models.IntegerField()
    user_real_name_th = models.CharField(max_length = 300)
    user_last_name_th = models.CharField(max_length = 300)

class PRPM_v_grt_pj_budget_eis(models.Model):
    psu_project_id = models.IntegerField()
    budget_group_desc = models.CharField(max_length = 50)
    budget_type_th = models.CharField(max_length = 50)
    budget_source_th =models.CharField(max_length = 50)
    budget_year = models.IntegerField()
    budget_amount = models.IntegerField()

class PRPM_ranking(models.Model):
    year = models.IntegerField()
    sco = models.IntegerField()
    isi = models.IntegerField()
    tci = models.IntegerField()
    # save_date = models.DateTimeField()

class PRPM_r_fund_type(models.Model):
    fund_type_id = models.IntegerField()
    fund_type_th = models.CharField(max_length = 300)
    fund_source_id = models.CharField(max_length = 2)
    fund_type_group = models.IntegerField()

