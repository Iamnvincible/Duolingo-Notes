import requests,json,time
from pathlib import Path

def user_fields(req_headers):
    '''
    fetch user info data
    '''
    if not req_headers:
        return None
    api_url = 'https://www.duolingo.com/2017-06-30/'
    userid = extract_userid(req_headers)
    if not userid:
        return None
    user_url = f'users/{userid}'
    timestamp = int(time.time()*1000)
    params = f"?fields=acquisitionSurveyReason,adsConfig,betaStatus,blockedUserIds,blockerUserIds,canUseModerationTools,classroomLeaderboardsEnabled,courses,creationDate,currentCourseId,email,emailAnnouncement,emailAssignment,emailAssignmentComplete,emailClassroomJoin,emailClassroomLeave,emailEditSuggested,emailEventsDigest,emailFollow,emailPass,emailPromotion,emailResearch,emailWeeklyProgressReport,emailSchoolsAnnouncement,emailSchoolsNewsletter,emailSchoolsProductUpdate,emailSchoolsPromotion,emailStreamPost,emailVerified,emailWeeklyReport,enableMicrophone,enableSoundEffects,enableSpeaker,experiments%7Bconnect_friends_quests_gifting_2,delight_lesson_taps_web,ginfra_web_disable_social_registration,gweb_capstone_xp_boost_reward_v2,gweb_friends_quests_main_v2,gweb_migrate_legendary_drawers,gweb_migrate_marketing_opt_in_drawers_v2,gweb_migrate_session_quit_drawers,gweb_mistake_progress_bar,gweb_redesign_onboarding_v3,gweb_redesign_red_dot,gweb_redesigned_page_footer,gweb_streak_nudge_session_end,gweb_tiered_daily_quests,gweb_time_spent_daily_quest,mcoach_family_weekly_report_dev,mcoach_web_legendary_per_node_gold_v2,mcoach_web_mistakes_list,minfra_web_stripe_setup_intent,path_web_path_change_notifications,path_web_sections,path_web_sections_v2,spack_web_fp_init_page,spack_web_hearts_new_users,spack_web_hearts_new_users_launch,spack_web_immersive_super_pf,spack_web_purchase_flow_redesign_23Q1,spack_web_purchase_flow_zero_cta,spack_web_registration_softwall_v2,web_hintable_text_rewrite_v3%7D,facebookId,fromLanguage,gemsConfig,globalAmbassadorStatus,googleId,hasFacebookId,hasGoogleId,hasPlus,health,id,inviteURL,joinedClassroomIds,lastResurrectionTimestamp,lastStreak%7BisAvailableForRepair,length%7D,learningLanguage,lingots,location,monthlyXp,name,observedClassroomIds,optionalFeatures,persistentNotifications,picture,plusDiscounts,practiceReminderSettings,privacySettings,referralInfo,rewardBundles,roles,sessionCount,streak,streakData%7BcurrentStreak,previousStreak%7D,timezone,timezoneOffset,totalXp,trackingProperties,username,webNotificationIds,weeklyXp,xpGains,xpGoal,zhTw,currentCourse&_={timestamp}"
    combined_url = f'{api_url}{user_url}{params}'
    #print(combined_url)
    response = requests.get(combined_url, headers=req_headers)
    if response.status_code == 200:
        user_info = response.text
        j_user_info = json.loads(user_info)
        with open('user_info.json', 'w') as f:
            json.dump(j_user_info, f, indent=4)
    else:
        print(response.status_code)

def get_vocabulary(headers_file, recent_voc_file, update=False):
    '''
    get all learned vocabulary
    '''
    if recent_voc_file and not update:
        print("using cached voc file")
        with open(recent_voc_file, 'r') as file:
            voc = json.load(file)
        return voc
    vocabulary_url = 'https://www.duolingo.com/vocabulary/overview'
    headers = process_header_file(headers_file)
    response = requests.get(vocabulary_url, headers=headers)
    if response.status_code == 200:
        voc_obj = json.loads(response.text)['vocab_overview']
        with open("voc.json", 'w') as file:
            json.dump(voc_obj, file, indent=4)
        return voc_obj
    else:
        print(response.status_code)
        return None
        
def process_header_file(header_file_path: str):
    file = Path(header_file_path)
    if file.exists():
        with file.open() as f:
            req_headers = f.readlines()
        headers = {}
        for header in req_headers:
            attr, value = [item.strip()
                           for item in header.split(':', maxsplit=1)][:2]
            headers[attr] = value
        return headers
    return None

def extract_userid(headers: dict):
    if headers and 'cookie' in headers.keys():
        cookie = headers['cookie']
        uuidkey = 'logged_out_uuid='
        uuidstart = cookie[cookie.rfind(uuidkey)+len(uuidkey):]
        uuidend = uuidstart.find(";")
        uuid = uuidstart[:uuidend]
        return uuid
    return None

if __name__ == "__main__":
    header_file = "headers"
    userinfo_file = "user_info.json"
    path_file = "path.json"
    skills_file = "skills.json"
    user_info = Path(userinfo_file)

    headers = process_header_file(header_file)
    #for key in headers.keys():
        #print(f'{key}:{headers[key]}')
    #print(headers)
    user_fields(headers)
