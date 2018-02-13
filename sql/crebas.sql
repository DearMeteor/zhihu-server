/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     2018/1/26 16:14:27                           */
/*==============================================================*/


drop table if exists account;

drop table if exists admin_user;

drop table if exists banner_info;

drop table if exists game_info;

drop table if exists key_value;

drop table if exists login_info;

drop table if exists portal;

drop table if exists publish_info;

/*==============================================================*/
/* Table: account                                               */
/*==============================================================*/
create table account
(
   id                   int not null auto_increment,
   game_id              int,
   role_id              varchar(64),
   app_id               int,
   server_id            int,
   service_id           int,
   account              varchar(32),
   vip_lv               int,
   vip_exp              int,
   score                int,
   name                 varchar(32),
   birthdate            date,
   phone                varchar(16),
   wechat               varchar(32),
   qq                   varchar(16),
   mail                 varchar(64),
   address              varchar(128),
   identity_number      varchar(32),
   primary key (id)
);

/*==============================================================*/
/* Table: admin_user                                            */
/*==============================================================*/
create table admin_user
(
   id                   int not null auto_increment,
   user_name            varchar(64),
   password             varchar(64),
   permission           text,
   real_name            varchar(64),
   primary key (id)
);

/*==============================================================*/
/* Table: banner_info                                           */
/*==============================================================*/
create table banner_info
(
   id                   int not null auto_increment,
   game_id              int,
   title                varchar(128),
   start_time           date,
   end_time             date,
   create_time          datetime,
   creator              varchar(128),
   img_url              varchar(256),
   link_url             varchar(256),
   status               int,
   style                varchar(128),
   primary key (id)
);

/*==============================================================*/
/* Table: game_info                                             */
/*==============================================================*/
create table game_info
(
   id                   int not null auto_increment,
   game_id              int,
   game_name            varchar(32),
   game_config          text,
   primary key (id)
);

/*==============================================================*/
/* Table: key_value                                             */
/*==============================================================*/
create table key_value
(
   id                   int not null auto_increment,
   s_key                varchar(128),
   s_value              varchar(128),
   types                varchar(128),
   orders              	int,
   primary key (id)
);

/*==============================================================*/
/* Table: login_info                                            */
/*==============================================================*/
create table login_info
(
   id                   int not null auto_increment,
   game_id              int,
   account              varchar(64),
   phone                varchar(32),
   ip                   varchar(16),
   last_login_time      datetime,
   primary key (id)
);

/*==============================================================*/
/* Table: portal                                                */
/*==============================================================*/
create table portal
(
   id                   int not null auto_increment,
   game_id              int,
   portal_name          varchar(128),
   link_url             varchar(256),
   img_url              varchar(256),
   status               int,
   primary key (id)
);

/*==============================================================*/
/* Table: publish_info                                          */
/*==============================================================*/
create table publish_info
(
   id                   int not null auto_increment,
   game_id              int,
   title                varchar(128),
   content              text,
   types                varchar(64) comment '发布类型。例如：游戏特权，服务特权，资讯中心，会员体系',
   creator              varchar(64),
   create_time          datetime,
   status               tinyint,
   style                varchar(256),
   orders              	int,
   info_prop            int comment '属性，匹配key_value表',
   info_type            int,
   is_now               tinyint,
   is_top               tinyint,
   img_url              varchar(256),
   primary key (id)
);

