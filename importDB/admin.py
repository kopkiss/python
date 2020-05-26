from django.contrib import admin
from .models import Get_db
from .models import Get_db_oracle
from .models import Prpm_v_grt_project_eis
from .models import PRPM_v_grt_pj_team_eis
from .models import PRPM_v_grt_pj_budget_eis
from .models import PRPM_ranking
from .models import PRPM_r_fund_type
from .models import PRPM_ranking_cited_isi




# Register your models here.
admin.site.register(Get_db)
admin.site.register(Get_db_oracle)
admin.site.register(Prpm_v_grt_project_eis)
admin.site.register(PRPM_v_grt_pj_team_eis)
admin.site.register(PRPM_v_grt_pj_budget_eis)
admin.site.register(PRPM_ranking)
admin.site.register(PRPM_r_fund_type)
admin.site.register(PRPM_ranking_cited_isi)



