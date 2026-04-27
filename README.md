# Store (aka LliureX-Store, aka Botiga)

Botiga is a GUI for [rebost engine](https://github.com/lliurex/rebost).
Its main purpose is to give an easy way for managing software.

## What differs Botiga from similar and (perhaps) better projects like Discover or Gnome-Software?

LliureX has some peculiarities that made existing App Stores not well suited for it:
- Zomandos (LliureX own installers) must be supported
- Included apps must be validated before they could be installed at classrooms
- Target users could be not tech savy nor gnu/linux users so concepts like "snap", "package", "flatpak", etc... must be avoided
- Installation and management must be as easy as possible for privileged users (teachers and staff) but impossible for students and restricted users
- There must be a mechanism to avoid all the restrictions as LliureX could be used at home
  
Botiga is desgined with those in mind.

## Usage 

As simply as search and install/remove applications. There're some caveats:

- An app can be installed only in one format although Botiga and Rebost are multiformat. This is an imposed restriction for avoiding duplicated applications in schools
- Applications in "Forbidden" or "Pending" states could not be installed in classrooms. "States" refer to the validation process at [appsedu](https://portal.edu.gva.es/appsedu/)
- As it relies on LliureX technologies and is designed with classroom requiriments in mind is not portable to other distros (sorry RedHat)

## Integration with appsedu

From [Appsedu portal](https://portal.edu.gva.es/appsedu/aplicacions-lliurex/) an application could be installed directly pressing the "Install in LliureX" button showed in approved applications.

## Integration with appstream

As with Appsedu, Botiga manages the appstream:// url-scheme provided by different portals like https://flathub.org or https://snapcraft.io 
