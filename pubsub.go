package cache

import (
	"context"
	"fmt"
)

type Message struct {
	SenderID string
	Key      string
}

func (c *Cache) startSubscriber(ctx context.Context) {
	ch := c.pubSub.Channel()

	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-ch:
			cacheMsg := toMessage(msg.Payload)

			if cacheMsg.SenderID == c.id {
				continue
			}

			c.local.Del(cacheMsg.Key)
		}
	}
}

func (c *Cache) Invalidate(ctx context.Context, key string) error {
	msg := Message{
		SenderID: c.id,
		Key:      key,
	}
	return c.redis.Publish(ctx, c.channel, msg.String()).Err()
}

func (m Message) String() string {
	return fmt.Sprintf("%s %s", m.SenderID, m.Key)
}

func toMessage(keyString string) Message {
	senderId := keyString[:16]
	key := keyString[17:]
	return Message{
		SenderID: senderId,
		Key:      key,
	}
}
