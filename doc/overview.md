
## data intro

Duolingo groups courses in *units*, each unit would have some topics which were called *skills* in Duolingo. Typically, one unit includes 2 skills to learn. Also, each unit includes several *levels*. A level includes some *lessons* and it is related to a skill. Some levels are special, like *chests*, *stories* and *practices*. How levels are organized in a unit is called a unit's *path*.

## userinfo

The user info api will tell us all things related to current user which includes user's name, user id, learning status, engaged language courses and so on. The most important part would be current course object `skills` which shows all infomation related to current language course, the learning path, all unit structures that can help us build up a learning map.

In `skills` section, study units are organized in *skills*. Each *skill* has its own name, may different from unit's name because Duo is still developing and organizing. Dating back to previous years, courses may organized in skills. I don't know, I had not using Duolingo then.

## vocabulary

The vocabulary api will tell us all recently seen words order by time. Cause all words are in it, we can process that into a vocabulary list. Though some words may occur in many units, it won't mess all. Key words in every unit won't be infected.

## parsing

Now that we have everything we may need, we can do parsing on the collected data.

### units

### skills
