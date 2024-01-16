from pathlib import Path
import json
import time
import requests


def user_fields(req_headers: dict, user_info: Path):
    """update user info object and save to json file

    Args:
        req_headers (dict): request headers
        user_info (Path): save file Path object

    Returns:
        _type_: user info json object
    """
    api_url = "https://www.duolingo.com/2017-06-30/"
    userid = extract_userid(req_headers)
    if not userid:
        return None
    user_url = f"users/{userid}"
    timestamp = int(time.time() * 1000)
    params = f"?fields=acquisitionSurveyReason,adsConfig,betaStatus,blockedUserIds,blockerUserIds,canUseModerationTools,classroomLeaderboardsEnabled,courses,creationDate,currentCourseId,email,emailAnnouncement,emailAssignment,emailAssignmentComplete,emailClassroomJoin,emailClassroomLeave,emailEditSuggested,emailEventsDigest,emailFollow,emailPass,emailPromotion,emailResearch,emailWeeklyProgressReport,emailSchoolsAnnouncement,emailSchoolsNewsletter,emailSchoolsProductUpdate,emailSchoolsPromotion,emailStreamPost,emailVerified,emailWeeklyReport,enableMicrophone,enableSoundEffects,enableSpeaker,experiments%7Bconnect_friends_quests_gifting_2,delight_lesson_taps_web,ginfra_web_disable_social_registration,gweb_capstone_xp_boost_reward_v2,gweb_friends_quests_main_v2,gweb_migrate_legendary_drawers,gweb_migrate_marketing_opt_in_drawers_v2,gweb_migrate_session_quit_drawers,gweb_mistake_progress_bar,gweb_redesign_onboarding_v3,gweb_redesign_red_dot,gweb_redesigned_page_footer,gweb_streak_nudge_session_end,gweb_tiered_daily_quests,gweb_time_spent_daily_quest,mcoach_family_weekly_report_dev,mcoach_web_legendary_per_node_gold_v2,mcoach_web_mistakes_list,minfra_web_stripe_setup_intent,path_web_path_change_notifications,path_web_sections,path_web_sections_v2,spack_web_fp_init_page,spack_web_hearts_new_users,spack_web_hearts_new_users_launch,spack_web_immersive_super_pf,spack_web_purchase_flow_redesign_23Q1,spack_web_purchase_flow_zero_cta,spack_web_registration_softwall_v2,web_hintable_text_rewrite_v3%7D,facebookId,fromLanguage,gemsConfig,globalAmbassadorStatus,googleId,hasFacebookId,hasGoogleId,hasPlus,health,id,inviteURL,joinedClassroomIds,lastResurrectionTimestamp,lastStreak%7BisAvailableForRepair,length%7D,learningLanguage,lingots,location,monthlyXp,name,observedClassroomIds,optionalFeatures,persistentNotifications,picture,plusDiscounts,practiceReminderSettings,privacySettings,referralInfo,rewardBundles,roles,sessionCount,streak,streakData%7BcurrentStreak,previousStreak%7D,timezone,timezoneOffset,totalXp,trackingProperties,username,webNotificationIds,weeklyXp,xpGains,xpGoal,zhTw,currentCourse&_={timestamp}"
    combined_url = f"{api_url}{user_url}{params}"
    response = requests.get(combined_url, headers=req_headers, timeout=10)
    if response.status_code == 200:
        j_user_info = json.loads(response.text)
        with user_info.open("w", encoding="utf-8") as f:
            json.dump(j_user_info, f, indent=4)
        return j_user_info
    else:
        print(response.status_code)
        return None


def get_vocabulary(headers: dict):
    """download all learnt vocabulary

    Args:
        headers (dict): request http header

    Returns:
        dict: all vocabulary in a json object
    """
    vocabulary_url = "https://www.duolingo.com/vocabulary/overview"
    response = requests.get(vocabulary_url, headers=headers, timeout=10)
    if response.status_code == 200:
        voc_obj = json.loads(response.text)["vocab_overview"]
        return voc_obj
    return None


def process_header_file(header_file_path: str):
    """read a http header file and squeeze it into a dict

    Args:
        header_file_path (str): http head file path

    Returns:
        dict: http head in dict structure
    """
    file = Path(header_file_path)
    if file.exists():
        with file.open() as f:
            req_headers = f.readlines()
        headers = {}
        for header in req_headers:
            attr, value = [item.strip() for item in header.split(":", maxsplit=1)][:2]
            headers[attr] = value
        return headers
    print("file is not exiting")
    return None


def extract_userid(headers: dict):
    """extract user id from cookie which lies in request headers

    Args:
        headers (dict): request header dict

    Returns:
        str: user id if exists or None
    """
    if headers and "cookie" in headers.keys():
        cookie = headers["cookie"]
        uuidkey = "logged_out_uuid="
        uuidstart = cookie[cookie.rfind(uuidkey) + len(uuidkey) :]
        uuidend = uuidstart.find(";")
        uuid = uuidstart[:uuidend]
        return uuid
    return None


def update_user_info(
    header_file: str = "headers",
    user_info_file: str = "user_info.json",
    force_update: bool = False,
):
    """download a user info object and return a json object

    Args:
        header_file (str, optional): a user http header file. Defaults to "headers".
        user_info_file (str, optional): a new or exiting json file to store user info. Defaults to "user_info.json".
        force_update (bool, optional): force download latest user info from duolingo or not if the user info file was saved beforehand. Defaults to False.

    Returns:
        dict: a json object representing user info
    """
    headers = process_header_file(header_file)
    user_info = Path(user_info_file)
    if not force_update and user_info.exists():
        with user_info.open("r", encoding="utf-8") as f:
            return json.load(f)
    elif headers:
        return user_fields(headers, user_info)
    else:
        return None


def update_vocabulary(
    header_file: str = "headers",
    cached_voc_file: str = "voc.json",
    force_update: bool = False,
):
    headers = process_header_file(header_file)
    cache = Path(cached_voc_file)
    if not force_update and cache.exists():
        print("using cached voc file")
        with cache.open("r", encoding="utf-8") as f:
            voc = json.load(f)
        return voc
    elif headers:
        voc = get_vocabulary(headers)
        with cache.open("w", encoding="utf-8") as f:
            json.dump(voc, f, indent=4)
        return voc
    else:
        return None


if __name__ == "__main__":
    file_path_prefix = "../res/"

    header_file = file_path_prefix + "headers"

    userinfo_file = file_path_prefix + "user_info.json"
    cached_voc_file = file_path_prefix + "voc.json"

    path_file = "path.json"
    skills_file = "skills.json"
    # First, download user info
    update_user_info(header_file, userinfo_file, True)
    # Second, download vocabulary
    update_vocabulary(header_file, cached_voc_file, True)
