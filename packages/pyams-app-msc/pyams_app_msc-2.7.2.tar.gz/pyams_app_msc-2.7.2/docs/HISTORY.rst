Changelog
=========

2.7.2
-----
 - renamed global alerts content provider
 - issue #184: added optional populations filter to scholar holidays periods getter

2.7.1
-----
 - updated theming dependencies: FontAwesome, FullCalendar, JSRender

2.7.0
-----
 - issue #184: added support for scholar holidays period
 - issue #186: manage groups permissions in movie theater session add form
 - issue #189: add support for theaters closure periods

2.6.10
------
 - updated calendar initialization process

2.6.9
-----
 - packaging issue

2.6.8
-----
 - issue #180: added session version in today program display
 - issue #181: updated planning display
 - updated PyAMS_scheduler task execution report format to Markdown

2.6.7
-----
 - updated importlib.resources dependency

2.6.6
-----
 - updated packaging

2.6.5
-----
 - issue #179: restrict selection to current movie theater when changing session activity

2.6.4
-----
 - issue #110: updated email messages content
 - issue #171: automatically adjust session duration when changing activity
 - issue #174: updated display of planned activity sessions
 - issue #176: added multiple selections to bookings advanced search form
 - issue #177: handle edit permission in session add form groups

2.6.3
-----
 - issue #168: removed workflow planning target sublocations adapter to avoid removal of planning
   events from catalog when a new version is removed

2.6.2
-----
 - issue #165: updated booking quotation getter

2.6.1
-----
 - issue #164: updated activity sessions dashboard
 - updated Gitlab-CI for Python 3.12

2.6.0
-----
 - added mobile application APIs
 - added sort order data attribute to activity sessions table
 - updated planning legend display
 - replaced permission predicate on views

2.5.3
-----
 - added toolbar action to display planning legend in a dropdown menu
 - added city to users profiles search engine
 - added movie theater selector view for external users on login
 - updated date display format in session change form and activity sessions dashboard
 - moved today program to planning feature module

2.5.2
-----
 - updated session edit form renderer

2.5.1
-----
 - issue #146: notify object modification on session activity change
 - issue #153: updated QR-Code button style and display
 - issue #154: updated profiles search and edit form access

2.5.0
-----
 - issue #134: updated display of today program
 - issue #139: updated display of activity sessions table
 - issue #143: added rooms capacity in planning view
 - issue #146: added option in planning contextual menu to change session's activity
 - issue #148: updated reminder message help
 - issue #150: added booking display modes to user profile
 - updates for last PyAMS_content API and JSON exporter interfaces

2.4.0
-----
 - issue #139: added activity sessions dashboard
 - issue #140: updated activity reservation period display

2.3.0
-----
 - issue #136: restrict booking principals selection
 - issue #137: added feature to extract and export user profiles information
 - issue #138: added feature to extract and export bookings information
 - added input mask to postal code
 - added support for fullscreen and layers selection controls in maps

2.2.1
-----
 - Updated GDAL support in Gitlab CI

2.2.0
-----
 - issue #129: updated calendar to always display current date
 - issue #133: added check for missing profiles in booking archiving task
 - issue #134: added option in operator profile to set today program length

2.1.0
-----
 - issue #122: add establishment name to session request notification message
 - issue #123: added timestamp argument to quotation link URL to avoid caching issues on quotation update
 - issue #124: handle unregistered users profiles in today program view
 - issue #126: add default quotation color if there is no defined color and no logo
 - issue #128: add audience contact fields in messages templates
 - issue #130: added separator in user profile menu between clients menus and operator menus

2.0.0
-----
 - issue #113: added notification and confirmation email messages on new booking requests
 - issue #115: updated session label getter for session without linked activity
 - issue #117: updated theater catalog pagination
 - issue #119: corrected translation
 - added property to activities to define booking period when no session is defined

1.99.14
-------
 - issue #103: add H3 and H4 title levels in activity description HTML editor
 - issue #104: update session capacity on room change in session add form
 - added option to notify user on profile creation by a site manager

1.99.13
-------
 - issue #100: updated template translation
 - issue #101: added attribute to define public sessions
 - issue #102: added movie theater API to get room information, and update session capacity on room change
 - updated required field marker position inside object widget
 - set principal ID in user profile on registration
 - added user registration confirmation delay in registration views adapter

1.99.12
-------
 - added booking property to store participants age

1.99.11
-------
 - issue #58: changed email address input mask
 - issue #61: memoize booking recipient establishment in booking properties when booking is archived
 - issue #81: updated activity specificities template to display sessions without visible illustration
 - issue #84: added quotation email property
 - issue #85: updated notification message handler on booking session change
 - issue #86: add missing principal_id attribute to principal annotations
 - issue #87: updated sessions display label when updating booking
 - issue #89: updated activity add form title terms factory to handle tags containing accents
   which were not extracted from TMDB
 - issue #91: updated ZMI today program template
 - issue #95: updated movie theater mail templates formatting values list

1.99.10
-------
 - add missing field to registration confirmation form
 - register factory for booking reminder task

1.99.9
------
 - issue #76: updated calendar styles
 - issue #78: register profile cleaner task factory
 - issue #80: added description field to activity info
 - issue #81: updated audiences management
 - added property to enable/disable new sessions requests for each activity
 - updated style of bookable sessions
 - updated session version getters

1.99.8
------
 - packaging/commit issue...

1.99.7
------
 - issue #33: allow recipient notification when session is changed for booking
 - issue #53: refresh dashboards after booking update
 - issue #56: added total seats count in booking add and edit forms
 - issue #60: quotation update
 - issue #62: manage deletion for rooms, audiences and prices
 - issue #67: update style of required fields in object widget
 - issue #68: problem with empty reminder messages
 - issue #69: updated datetime picker styles
 - issue #71: added property to set the number of weeks for which to display sessions in calendar portlet renderer
 - issue #72: removed end time from session label
 - added rotation effect to filters switchers
 - updated navigation link style
 - use factories to create scheduler tasks
 - replaced "datetime.utcnow()" with "datetime.now(timezone.utc)"
 - updated CSS styles and other minor corrections

1.99.6.2
--------
 - added missing Javascript resources to Git

1.99.6.1
--------
 - packaging issue

1.99.6
------
 - added paragraphs support to movie theaters
 - added workflow publication support to movie theaters
 - updated skin colors and styles
 - display warning message when removing session with bookings
 - updated header logo getter
 - pre-select audience on new booking request
 - added movie theater SEO adapter
 - updated calendar event target URL
 - added link to catalog entry data from session booking form
 - updated refresh callbacks after booking workflow status update

1.99.5.1
--------
 - added control in page header renderer

1.99.5
------
 - issue #33: allow recipient notification when session is changed for booking
 - issue #34: automatically update sesion capacity when moved to a new room with higher capacity
 - issue #35: update dashboard on booking update
 - added user profile views
 - updated portlets and renderers for menus, navigation and styles

1.99.4
------
 - issue #27: added theater setting to set first week day displayed in calendars
 - issue #30: updated actions used to update content illustrations from medias gallery
 - issue #31: added free accompanists count in booking data
 - issue #32: allow direct booking validation from creation form
 - updated event title getter
 - updated user profile edit form
 - added column priority getter for use in responsive tables

1.99.3
------
 - issue #21: added display of principal phone number
 - issue #22: updated shared content header viewlet to add button to go back to dashboard
 - issue #25: updated prompt of activity selection widget
 - issue #26: added support for vertical synchronization of calendars
 - issue #27: removed theater week view from calendar
 - issue #30: added action to set content illustration from medias gallery image
 - issue #31: updated accompagnists price handler in quotations

1.99.2.4
--------
 - removed code dependency on OAuth authentication module (bis!)

1.99.2.3
--------
 - removed code dependency on OAuth authentication module

1.99.2.2
--------
 - updated tests requirements

1.99.2.1
--------
 - issue #24: updated booking value getter in dashboards

1.99.2
------
 - updated menus order
 - added paragraphs factory settings support to movie theater
 - updated booking recipient label
 - added structure type attribute to user profile
 - disable autocomplete on user profile creation form
 - added structures types references table
 - renamed MSC skin
 - updated movie theater breadcrumbs
 - added marker interface to user dashboard views
 - updated translations
 - updated session seats
 - updated session label adapter
 - added button in booking add form to automatically redirect to validation form after creation
 - updated AJAX finder URL to only get activities declared inside movie theater
 - removed unused fields from address
 - added tooltips on calendar events
 - added permission and role to manage references tables
 - allow theater manager to assign role to other managers
 - include TMDB images as gallery paragraph instead of global gallery
 - removed gallery support on catalog entries
 - disabled paragraphs associations menu
 - updated illustrations adapters
 - updated activity types forms (fixes issue #6)
 - added condition on bookings button display
 - added missing picture to Git
 - updated theater planning menu position

1.99.1
------
 - added edit forms content getters
 - added custom catalog entry roles adapters
 - removed roles restrictions menu entries from theater navigation menu
 - removed source folder from movie theater activity types properties (issue #6)
 - changed reminder delay unit from hours to days (issue #4]
 - updated theater settings edit form (issue #4)

1.99.0.1
--------
 - fixed packaging issue

1.99.0
------
 - first preliminary release
