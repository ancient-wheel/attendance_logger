---
title: Attendance logger. REST API protocol
subtitle: version 1.0.0
author: Andrey Antiporovich
date: January 2026
---

# Introduction

I develope this API protocol as a part of my pet project. This web application for logging attendance shell support a children's education club. This club helps families with children with mental and physical disabilities.

# Assumptions

Endpoints response with a json.
Backend doesn’t redict between endpoints, so it must be done by frontend.

# Roles and permission levels

Known roles are

| Role | Permission’s level | Description |
| --- | :---: | --- |
| Unauthorized user	| 0 | Any user in world wide web |
| Unconfirmed user | 1 | User after registration, but before the email address in the registration form is confirmed | 
|Inactive user | 1 | User with deactivated account |
| User | 2 | User who confirmed its email address |
| Employee | 3 | A user after an update by head manager or higher role. A employee of the service. |
| Manager | 4 |	Employee with special rights after an upgrade by head manager or higher role
| Head manager | 5 | Manager with special rights after an upgrage by owner or admin |
| Owner | 6 | Owner has all permissions regarding service and application. Doesn’t have technical background, but can promote a user to admin. A downgrade of an owner by admin require a confirmation by owner. |
| Admin | 7 | God of the application. Admin can promote a user to owner, but for a demotion require a confirmation by owner. |

Permissions increase from top to buttom.

# Endpoints

Scheme for endpoints
    
    <root>/api/v<api-version>/<endpoints>

This scheme looks like this `<root>/api/v1/<endpoint>` for first vesion of the protocol.
    
## Main

> to be defined

Purpose of the main page is not defined and not used yet. Highly likely it shell present general information about the club. 

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/` | Show home page. | 0+ | 

## Authentication

Authentification is basen on "Authentification Bearer" method. Frontend is responcible for logout processG`.

| Methods | Endpoints | JSON fields <br>  * optional fields | Description | Permissions level |
| --- | --- | --- | --- | :---: |
| POST | `/auth/register` | <ul> <li> **username**: string</li> <li>**email**: string</li> <li>**password**: string</li> </ul> | Add new user | 0+ |
| POST | `/auth/login` | <ul> <li> **email**: string</li> <li> **password**: string</li> </ul> | Process user’s login | 0+ | 
| GET | `/auth/logout`|  | Process user’s logout | 2+ | 
| POST | `/auth/confirmation` | <ul> <li> **username**: string </li> <li> **email**: string </li> </ul> | Request a link with a token to varify email | 1+ |
| GET | `/auth/email/<token>` | | Confirm email address with a unique `<token>` | 0+ |

## Users

| Methods | Endpoints | JSON fields <br> * optional fields | Description | Permissions level |
| ---   | --- | --- | --- | :---: | 
| GET | `/users` | | Request total list of users <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> </ul> | 4+ | 
| POST  | `/users` | <ul> <li> **username**: string </li> <li> **email**: string </li> <li> **password**: string </li> <li> **roles**: string </li> <li> **groups**: list[`<group_id>` *as* integer] </li> </ul> | Add new user | 5+ |
| GET | `/users/<id>` | | Show profile for user `<id>` | 2+ |
| PUT | `/users/<id>` | <ul> <li> **user_id**: integer </li> <li> **username**: string </li> <li> **active**: boolean </li> <li> **roles**: string </li> <li> **groups**: list[`<group_id>` *as* integer ] </li>  <li> **favorites**: <br> dict[ <ul> <li> *"lessons"*: list[`<lesson_id>` *as* integer] </li> <li> *"groups"*: list[`<group_id>` *as* integer] </li> </ul> ] </li> </li> </ul> | Edit profile for user `<id>` | 2+ |
| POST | `/users/<id>/favorities` | <ul> <li> **user_id**: integer </li> <li> **favorites**: <br> dict[ <ul> <li> *"lessons"*: list[`<lesson_id>` as *integer*] </li> <li> *"groups"*: list[`<group_id>` *as* integer] </li> </ul> ] </li> </ul> | Show favorite groups and lessons for the user `<id>` | 2+ |
| PUT | `/users/<id>/favorites` | <ul> <li> **user_id**: integer </li> <li> **favorites**: <br>  dict[ <ul> <li> *"lessons"*: list[`<lesson_id>` *as* integer] </li> <li> *"groups"*: list[`<group_id>` *as* integer] </li> </ul> ] </li> </ul> | Update favorites groups and lessons for user `<id>` | 2+ |

## Clients, contracts and subscriptions

| Methods | Endpoints | JSON fields <br> * optional fields | Description | Permissions level |
| --- | --- | --- | --- | :---: | 
| GET | `/clients` || Request list of clients <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> <li> **sort** for sorting results with leading `+` or `-` for ascending or descenting order</li> </ul> | 3+ | 
| POST | `/clients` | <ul> <li> **name**: string </li> <li> **child_name**: string </li> <li> **address**: string </li> <li> **phone**: string </li> <li> **childs_birthday**: `YYYY-MM-DD`*as* string </li> <li> **contracts** *: list[`<contract_id>` *as* integer] </li> <li> **subscriptions** *: list[`<subscription_id>` *as* integer] </li> <li> **notes** *: string </li> </ul> | Add new client | 3+ |
| GET | `/clients/<id>` || Show profile for client `<id>` | 3+ | 
| GET | `/contracts` || Get list of contracts <br> optional parameters: <ul> <li> **client** -- client's `<id>`</li> <li> **date_from** -- filter out results older then given date </li> <li> **date_untill** -- filter out results newer then given date </li> <li> **page** -- paging results with 20 items per page </li> </ul> |  |
| POST | `/contracts` | <ul> <li> **number** *: string </li> <li> **client_id**: integer </li> <li> **signed_on** *: `YYYY-MM-DD`*as* string </li> <li> **canceled_on** *: `YYYY-MM-DD`*as* string </li> </ul> | Add new contract | 3+ |
| GET | `/contracts/<id>` || Get contract `<id>` | 3+ |
| PUT | `/contracts/<id>` | <ul> <li> **active**: boolean </li> <li> **signed_on**: `YYYY-MM-DD`*as* string </li> <li> **canceled_on**: `YYYY-MM-DD`*as* string </li> </ul>  | Edit contract `<id>` | 3+ |
| GET | `/subscriptions` || Show subscriptions <br> optional parameters: <ul> <li> **client_id** -- client's `<id>` </li> <li> **contract_id** -- contract's `<id>` </li>  <li> **date_from** -- filter out results older then given date </li> <li> **date_from** -- filter out results newer then given date </li> <li> **page** -- paging results with 20 items per page </li> </ul> | 3+ |
| POST | `/subscriptions` | <ul> <li> **client_id**: integer </li> <li> **full_price_id**: integer </li> <li> **discount_percent** *: integer </li> </ul>  | Add new subscription | 3+ |
| PUT | `/subscriptions/<id>` | <ul> <li> **end_date** *: `YYYY-MM-DD` *as* string </li> <li> **freezed**: bool </li> <li> **visits** *: list[`<visit_id>` *as* integer] </li> </ul>  | Edit subscription `<id>` | 3+ |
<!-- | GET | `/clients/<id>/contracts` | Show all contracts of the client `<id>`
| GET | `/clients/<id>/subscriptions` | Show all subscriptions of the client `<id>` | | -->

## Groups and lessons

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/groups` | Request total list of groups <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> <li> **sort** for sorting results with leading + or – for ascending or descenting order</li> </ul> |  | 
| POST | `/groups` | Add new group |  | 
| GET | `/groups/<id>` | Get information about group ID |  | 
| PUT | `/groups/<id>` | Edit group with ID equal to `<id>` |  | 
| GET | `/groups/<id>/lessons` | Request total list of lessons for the group `<id>` <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> <li> **sort** for sorting results with leading + or – for ascending or descenting order</li> </ul> |  | 
| POST | `/groups/<id>/lessons` | Add new lesson to group `<id>` |  | 
| GET | `/groups/<id>/lessons/<id>` | Get information about a lesson `<id>` |  |
| PUT | `/groups/<id>/lessons/<id>` | Edit lesson `<id>` |  |
| GET | `/lessons/<id>/attendance` | Get information about participants of the current lesson |  |
| PUT | `/lessons/<id>/attendance` | Update attendance for a lesson `<id>` |  |

## Prices

Endpoints for settings prices. Head manager and higher role can edit prices.

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/prices` | Request total list of prices. <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> <li> **sort** for sorting results with leading + or – for ascending or descenting order</li> </ul> | 0+ | 
| POST | `/prices` | Add new price | 5+ |
| PUT | `/prices/<id>` | Edit price `<id>` | 5+ |

## Statistics

Summary of setup statistics. Employee can view some statistics regarding her/his groups. Manager can see some statistics regarding employees and groups. All statistics are accessable by head manager and higher role.

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/statistics` | Get main statistics overview | (3+) <br> 5+ |
| GET | `/statistics/employees` | Get  statistics overview about employees | 4+ |
| GET | `/statistics/employees/<id>` | Get  statistics overview about employee `<id>` | 3+ |
| GET | `/statistics/locations` | Get  statistics overview about locations | 5+ |
| GET | `/statistics/locations/<id>` | Get  statistics overview about location `<id>` | 5+ |
| GET | `/statistics/groups` | Get  statistics overview about groups | (3+) <br> 4+ |
| GET | `/statistics/groups/<id>` | Get  statistics overview about group `<id>` | 3+ |

# Responses

This chapter deals with possible reponses from server.

## Codes in use

Known codes are

<!-- | 201 | Created | Request has led to the creation of a resource | -->

| Status | Message | Description |
| :---: | --- | --- |
| 200 | OK | Request has succeeded |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Lacks valid authentication credentials |
| 403 | Forbidden | Insufficient permissions to a resource or action |

## Schemes

Following responses don't depend on endpoint.

`200`

    {
        "status": "OK"
    }

`400` 

    {
        "status": "Bad Request", 
        "message": "Missing fields."
    }

`403`

    {
        "status": "Forbidden",
        "message": "Insufficient Permissions."
    }

### Endpoints *auth*

`200`


    {
        "status": "OK",
        "access_token": "<string>"
    }

`400`

    {
        "status": "Bad Request", 
        "messages":
        {
            "username": "Username is required.",  // optional
            "email": "Email failed validation.",  // optional
            "email": "Email already registered.", // optional
            "password": "Password must contain at least of 12 and maximum 128 characters."  // optional
        }
    }

    {
        "status": "Bad Request", 
        "message": "Invalid credentials."
    }

    {
        "status": "Bad Request", 
        "message": "Invalid or expired confirmation token."
    }

    {
        "status": "Bad Request", 
        "message": "Email is already confirmed."
    }
