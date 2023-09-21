import time
from pathlib import Path
import requests
import json


def user_fields(req_headers):
    if not req_headers:
        return None
    api_url = 'https://www.duolingo.com/2017-06-30/'
    userid = extract_userid(req_headers)
    if not userid:
        return None
    user_url = f'users/{userid}'
    timestamp = int(time.time()*1000)
    params = f"?fields=acquisitionSurveyReason,adsConfig,betaStatus,blockedUserIds,blockerUserIds,canUseModerationTools,classroomLeaderboardsEnabled,courses,creationDate,currentCourseId,email,emailAnnouncement,emailAssignment,emailAssignmentComplete,emailClassroomJoin,emailClassroomLeave,emailEditSuggested,emailEventsDigest,emailFollow,emailPass,emailPromotion,emailResearch,emailWeeklyProgressReport,emailSchoolsAnnouncement,emailSchoolsNewsletter,emailSchoolsProductUpdate,emailSchoolsPromotion,emailStreamPost,emailVerified,emailWeeklyReport,enableMicrophone,enableSoundEffects,enableSpeaker,experiments%7Bconnect_friends_quests_gifting_2,courses_en_te_v1,courses_xh_en_experiment,gen_sess_web_underline_mistake,gweb_capstone_xp_boost_reward_v2,gweb_friends_quests,gweb_mistake_progress_bar,gweb_redesigned_page_footer,mcoach_family_weekly_report_dev,mcoach_web_legendary_per_node_gold_v2,mcoach_web_mistakes_list,minfra_web_stripe_setup_intent,path_web_sections,spack_web_fp_init_page,spack_web_hearts_existing_users,spack_web_hearts_new_users,spack_web_hearts_new_users_launch,spack_web_immersive_super_pf,spack_web_immersive_super_shop_pf,spack_web_practice_fab_new_users,spack_web_purchase_flow_redesign_23Q1,spack_web_registration_softwall_v2,tsl_child_user_leaderboard,web_match_sparkles%7D,facebookId,fromLanguage,gemsConfig,globalAmbassadorStatus,googleId,hasFacebookId,hasGoogleId,hasPlus,health,id,inviteURL,joinedClassroomIds,lastResurrectionTimestamp,lastStreak%7BisAvailableForRepair,length%7D,learningLanguage,lingots,location,monthlyXp,name,observedClassroomIds,optionalFeatures,persistentNotifications,picture,plusDiscounts,practiceReminderSettings,privacySettings,referralInfo,rewardBundles,roles,sessionCount,streak,streakData%7BcurrentStreak,previousStreak%7D,timezone,timezoneOffset,totalXp,trackingProperties,username,webNotificationIds,weeklyXp,xpGains,xpGoal,zhTw,currentCourse&_={timestamp}"
    combined_url = f'{api_url}{user_url}{params}'
    print(combined_url)
    response = requests.get(combined_url, headers=req_headers)
    if response.status_code == 200:
        user_info = response.text
        j_user_info = json.loads(user_info)
        with open('user_info.json', 'w') as f:
            json.dump(j_user_info, f, indent=4)
    else:
        print(response.status_code)


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


def get_skills(userinfo: str):
    file = Path(userinfo)
    if file.exists():
        with file.open() as f:
            userinfo = json.load(f)
        skills = userinfo['currentCourse']['skills']
        with open("skills.json", "w") as f:
            json.dump(skills, f, indent=4)


def get_path(userinfo: str):
    file = Path(userinfo)
    if file.exists():
        with file.open() as f:
            userinfo = json.load(f)
        path = userinfo['currentCourse']['path']
        with open("path.json", "w") as f:
            json.dump(path, f, indent=4)


def get_units(path: str):
    file = Path(path)
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path('units')
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open() as f:
            units = json.load(f)
        for unit in units:
            u = {}
            u["index"] = unit['unitIndex'] + 1
            u["guide"] = unit['guidebook']
            u['theme'] = unit['teachingObjective']
            u['cert'] = unit['cefrLevel']
            u['levels'] = []
            for level in unit['levels']:
                if level['type'] == "skill" and level['pathLevelClientData']['skillId'] not in sub_teachingobjectives:
                    sub_teachingobjectives.append(
                        level['pathLevelClientData']['skillId'])
                    u['levels'].append(level)
            unit_path = Path(f'unit_{u["index"]}.json')
            unit_file = Path(save_dir, unit_path)
            with unit_file.open("w") as file:
                json.dump(u, file, indent=4)


def get_skills(skills: str):
    file = Path(skills)
    if file.exists():
        sub_teachingobjectives = []
        save_dir = Path('skills')
        if not save_dir.exists():
            save_dir.mkdir()
        with file.open() as f:
            skill_list = json.load(f)
        for arr in skill_list:
            for item in arr:
                skill_title = item['urlName']
                skill_path = Path(f'{skill_title}.json')
                skill_file = Path(save_dir, skill_path)
                with skill_file.open("w") as file:
                    json.dump(item, file, indent=4)


if __name__ == "__main__":
    header_file = "headers"
    userinfo_file = "user_info.json"
    path_file = "path.json"
    skills_file = "skills.json"
    user_info = Path(userinfo_file)
    if user_info.exists():
        skills = Path(skills_file)
        path = Path(path_file)
        if not skills.exists():
            get_skills(userinfo_file)
        if not path.exists():
            get_path(userinfo_file)
    else:
        headers = process_header_file(header_file)
        user_fields(headers)
    # get_units(path_file)
    get_skills(skills_file)
