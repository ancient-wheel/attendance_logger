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

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: |
| POST | `/auth/register` | Add new user | 0+ | 
| POST | `/auth/login` | Process user’s login | 0+ | 
| GET | `/auth/logout` | Process user’s logout | 2+ | 
| POST | `/auth/confirmation` | Request a confirmation token to specific email | 1+ |
| GET | `/auth/email/<token>` | Confirm email address with a unique <token> | 0+ |

## Users

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/users` | Request total list of users <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> </ul> |  | 
| POST | `/users` | Add new user |  |
| GET | `/users/<id>` | Show user’s profile for user with ID equal to <id> |  |
| PUT | `/users/<id>` | Edit user’s profile with user ID equal to `<id>` |  |
| POST | `/users/<id>/favorities` | Show favorite groups and lessons of the user |  |
| PUT | `/users/<id>/favorites` | Update favorites groups and lessons |  |

## Clients, contracts and subscriptions

| Methods | Endpoints | Description | Permissions level |
| --- | --- | --- | :---: | 
| GET | `/clients` | Request total list of clients <br> optional parameters: <ul> <li> **page** for paging the results with 20 items per page </li> <li> **sort** for sorting results with leading + or – for ascending or descenting order</li> </ul> |  | 
| GET | `/clients/<id>` | Show client’s profile for client with ID equal to `<id>` |  | 
| GET | `/clients/<id>/contracts` | Show all contracts of the client `<id>`
| GET | `/clients/<id>/subscriptions` | Show all subscriptions of the client `<id>` | |
| GET | `/contracts` | Show all contracts |  |
| POST | `/contracts` | Add new contracts |  |
| PUT | `/contracts/<id>` | Add new contracts |  |
| GET | `/subscriptions` | Show all subscriptions |  |
| POST | `/subscriptions` | Add new subscription |  |
| PUT | `/subscriptions/<id>` | Edit subscription `<id>` |  |

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

### Register

#### 200

    {
        "status": "OK"
    }

    {
        "status": "OK"
        "message": "<string>"
    }

#### 400

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
