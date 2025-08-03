from enum import Enum

class JobContext(str, Enum):
    BLOG = "blog"
    LINKED_IN_POST = "linked_in_post"
    TWITTER_POST = "twitter_post"
    REDDIT_POST = "reddit_post"
    FACEBOOK_POST = "facebook_post"
    COMMENT_SENTIMENT_ANALYSIS = "comment_sentiment_analysis"
    COMMENT_IDEA_GENERATION = "comment_idea_generation"
    COMMENT_ANALYSIS = "comment_analysis"

    def __str__(self):
        return self.value