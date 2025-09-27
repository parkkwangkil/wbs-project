from .models import AdCampaign

def ads_context(request):
    """
    사이드바에 표시할 광고를 가져오는 context processor
    """
    if request.user.is_authenticated:
        # 사용자의 구독 상태에 따라 광고 표시 여부 결정
        try:
            user_subscription = request.user.usersubscription_set.filter(is_active=True).first()
            if user_subscription and user_subscription.plan.name == 'Free':
                # 무료 플랜 사용자에게만 광고 표시
                sidebar_ads = AdCampaign.objects.filter(is_active=True)[:3]
                return {'sidebar_ads': sidebar_ads}
        except:
            pass
    
    return {'sidebar_ads': []}


