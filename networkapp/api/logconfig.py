log_config = {
   "version": 1,
   "disable_existing_loggers": False,
   "formatters": {
      "simple": {
         "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      }
   },
   "handlers": {
      "console": {
         "class": "logging.StreamHandler",
         "level": "INFO",
         "formatter": "simple",
         "stream": "ext://sys.stdout"
      }
   },
   "loggers": {
      "simpleExample": {
         "level": "INFO",
         "handlers": [
            "console"
         ],
         "propagate": "no"
      },
      "default": {
         "level": "INFO",
         "handlers": [
            "console"
         ],
         "propagate": "yes"
      }
   },
   "root": {
      "level": "INFO",
      "handlers": [
         "console"
      ]
   }
}