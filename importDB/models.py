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


# class Oracle_v_grt_project_eis(models.Model):
#     PSU_PROJECT_ID = models.IntegerField()
#     RDO_PROJECT_ID = models.IntegerField()
#     USER_ID_CARD,
#     STAFF_ID = models.IntegerField()
#     SUBMIT_NAME_SURNAME_TH,
#     PJ_STATUS_ID = models.IntegerField()
#     PJ_STATUS_TH,
#     CREATE_DATE,
#     SUBMIT_DATE,
#     USER_UPDATE,
#     LAST_UPDATE,
#     FUND_ID,
#     FUND_TH,
#     FUND_BUDGET_YEAR,
#     FUND_SOURCE_ID,
#     FUND_SOURCE_TH,
#     FUND_TYPE_ID,
#     FUND_TYPE_TH,
#     FUND_TYPE_KIND,
#     FUND_ROUND_NO,
#     PROJECT_TYPE_ID,
#     PROJECT_TYPE_TH,
#     PSU_PARENT_PROJECT_ID,
#     PROJECT_TOTAL,
#     SUB_PROJECT_NO,
#     PROJECT_STATUS_ID,
#     PROJECT_STATUS,
#     CONTINUE_YEAR_NO,
#     PROJECT_CONTINUE,
#     NO_OF_YEAR,
#     CONTINUE_PROJECT_ID,
#     FACULTY_OWNER_ID,
#     FACULTY_OWNER,
#     CAMP_OWNER_ID,
#     CAMP_OWNER,
#     PROJECT_NAME_TH,
#     PROJECT_NAME_EN,
#     PROJECT_KEYWORD,
#     PROJECT_START_DATE,
#     PROJECT_END_DATE,
#     PROJECT_EXTEND_DATE,
#     PROJECT_YEAR_INTERVAL,
#     PROJECT_MONTH_INTERVAL,
#     CORRESPONDING_EMAIL,
#     NEW_RESEACRHER,
#     NEW_RESEACRHER_DESC,
#     RESEARCH_TYPE_ID,
#     RESEARCH_TYPE_TH,
#     ACADEMIC_BRANCH_ID,
#     ACADEMIC_BRANCH_TH,
#     RESEARCH_AREA_ID,
#     RESEARCH_AREA_TH,
#     STRATEGIC20_TYPE_ID,
#     STRATEGIC20_TYPE_TH,
#     STRATEGIC20_ID,
#     STRATEGIC20_TH,
#     PSU_STRATEGIC_ID,
#     PSU_STRATEGIC_TH,
#     RESEARCH_ISSUES,
#     PSU_RESEARCH_AREA_ID,
#     PSU_RESEARCH_AREA_TH,
#     PSU_ACADEMIC_BRANCH_ID,
#     PSU_ACADEMIC_BRANCH_TH,
#     NO_RCN,
#     RCN_ID,
#     RCN_TH,
#     RCN_TYPE_ID,
#     PSU_GRADUATE_TYPE,
#     PSU_FOREIGN_RESEARCH,
#     PSU_EXTERNAL_RESEARCH,
#     PSU_CAMPUS_RESEARCH,
#     PROJECT_REMARK,
#     PROJECT_GMO_USED,
#     PROJECT_ANIMAL_USED,
#     PROJECT_PLANT_USED,
#     PLANT_FORCOMMERCE,
#     PROJECT_HUMAN_USED,
#     PROJECT_PATHOGEN_USED,
#     PROJECT_CHEMICAL_USED,
#     LAB_CHECKLIST,LAB_NO,
#     PROJECT_GROUP_ID,
#     PROJECT_GROUP_TH,
#     CROSS_OWNER,
#     PROJECT_NOTE,
#     RELATIVE_PROJECT_ID,
#     RELATIVE_OWNER_ID,
#     LEADER_USER_ID_CARD,
#     LEADER_STAFF_ID,
#     LEADER_NAME_SURNAME_TH,
#     LEADER_FACULTY_ID,
#     LEADER_FACULTY,
#     LEADER_DEPARTMENT_ID,
#     LEADER_DEPARTMENT,
#     SUM_REQ_ALL,
#     SUM_REC_ALL,
#     SUM_REC_PER,
#     SUM_BUDGET_PLAN,
#     INT_BUDGET_YEAR,
#     INTEGRATION_TH,
#     INTEGRATION_TYPE_TH,
#     INTEGRATION_TYPE_SUB_TH,
#     FLAG_AREA_DESC,
#     PSU_INTEGRATION_PLAN_TH,
#     PLAN_FULL_NAME_TH,
#     PROJECT_REPRINT_DATE,
#     PROJECT_OUTPUT_DATE,
#     PROJECT_DRAF_DATE,
#     PROJECT_FINAL_DATE,
#     PROJECT_TERMINATE_DATE,
#     PROJECT_TERMINATE_REMARK,
#     PROJECT_FINISH_DATE,
#     FLAG_REPORT

    