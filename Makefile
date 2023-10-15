deploy:
	sam deploy --template-file template.yaml --stack-name $(STACK_NAME) --parameter-overrides MediaBucket=$(MEDIA_BUCKET) --capabilities CAPABILITY_IAM
