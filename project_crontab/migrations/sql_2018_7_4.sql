use cmdb;
CREATE TABLE `asset_cron_minion` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `name` varchar(32) NULL);
ALTER TABLE `asset_cron_minion` ADD COLUMN `saltminion_id` integer NOT NULL;
ALTER TABLE `asset_cron_minion` ALTER COLUMN `saltminion_id` DROP DEFAULT;

ALTER TABLE `asset_crontab_svn` ADD COLUMN `minion_hostname_id` integer NOT NULL;
ALTER TABLE `asset_crontab_svn` ALTER COLUMN `minion_hostname_id` DROP DEFAULT;

CREATE INDEX `asset_crontab_svn_30148987` ON `asset_crontab_svn` (`minion_hostname_id`);
ALTER TABLE `asset_crontab_svn` ADD CONSTRAINT `asset_cronta_minion_hostname_id_0ea6b0e5_fk_asset_cron_minion_id` FOREIGN KEY (`minion_hostname_id`) REFERENCES `asset_cron_minion` (`id`);
CREATE INDEX `asset_cron_minion_3ee7e84d` ON `asset_cron_minion` (`saltminion_id`);
ALTER TABLE `asset_cron_minion` ADD CONSTRAINT `asset_cron_minion_saltminion_id_f996dbf4_fk_asset_minion_id` FOREIGN KEY (`saltminion_id`) REFERENCES `asset_minion` (`id`);



CREATE TABLE `project_crontab_crontabcmd` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `cmd` longtext NOT NULL, `auto_cmd` longtext NOT NULL, `frequency` varchar(16) NOT NULL, `cmd_status` integer NOT NULL, `create_time` datetime(6) NULL, `update_time` datetime(6) NULL, `last_run_result` varchar(16) NULL, `last_run_time` datetime(6) NULL, `creator_id` integer NOT NULL, `svn_id` integer NOT NULL, `updater_id` integer NULL);
ALTER TABLE `project_crontab_crontabcmd` ADD CONSTRAINT `project_crontab_crontabcmd_creator_id_4d1261f5_fk_auth_user_id` FOREIGN KEY (`creator_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `project_crontab_crontabcmd` ADD CONSTRAINT `project_crontab_crontabc_svn_id_19b43599_fk_asset_crontab_svn_id` FOREIGN KEY (`svn_id`) REFERENCES `asset_crontab_svn` (`id`);
ALTER TABLE `project_crontab_crontabcmd` ADD CONSTRAINT `project_crontab_crontabcmd_updater_id_5cccc316_fk_auth_user_id` FOREIGN KEY (`updater_id`) REFERENCES `auth_user` (`id`);

commit;