package cache_sync

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"github.com/dgraph-io/ristretto/v2"
	"github.com/redis/go-redis/v9"
	"time"
)

func generateID() string {
	bytes := make([]byte, 8)
	_, _ = rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

type Cache struct {
	id      string
	redis   *redis.Client
	pubSub  *redis.PubSub
	local   *ristretto.Cache[string, any]
	channel string
	cancel  context.CancelFunc
	ttl     time.Duration
}

type Config struct {
	// Redis
	RedisAddr string
	Channel   string

	// Ristretto
	LocalMaxCost     *int64
	LocalNumCounters *int64

	// TTL
	TTL *time.Duration
}

func New(cfg Config) (*Cache, error) {
	var localMaxCost int64
	if cfg.LocalMaxCost == nil {
		localMaxCost = 1 << 30
	} else {
		localMaxCost = *cfg.LocalMaxCost
	}

	var localNumCounters int64
	if cfg.LocalNumCounters == nil {
		localNumCounters = localMaxCost * 10
	} else {
		localNumCounters = *cfg.LocalNumCounters
	}

	local, err := ristretto.NewCache(&ristretto.Config[string, any]{
		NumCounters: localNumCounters,
		MaxCost:     localMaxCost,
		BufferItems: 64,
	})

	if err != nil {
		return nil, err
	}

	client := redis.NewClient(&redis.Options{
		Addr: cfg.RedisAddr,
	})

	pubSub := client.Subscribe(context.Background(), cfg.Channel)

	ctx, cancel := context.WithCancel(context.Background())

	TTL := time.Hour * 24
	if cfg.TTL != nil {
		TTL = *cfg.TTL
	}

	c := &Cache{
		id:      generateID(),
		redis:   client,
		pubSub:  pubSub,
		local:   local,
		channel: cfg.Channel,
		cancel:  cancel,
		ttl:     TTL,
	}

	go c.startSubscriber(ctx)

	return c, nil
}

// Get retrieves a value from the local cache.
// If not exists, it returns (nil, false).
func (c *Cache) Get(key string) (any, bool) {
	return c.local.Get(key)
}

// Set stores a value int the local cache and publishes an invalidation message
// to other servers via Redis Pub/Sub.
func (c *Cache) Set(key string, value any) error {
	c.local.SetWithTTL(key, value, 1, c.ttl)

	// TODO: publish other servers
	return nil
}

// Delete removes a value from the local cache and publishes an invalidation message
// to other servers via Redis Pub/Sub.
func (c *Cache) Delete(key string) error {
	c.local.Del(key)

	// TODO: publish other servers
	return nil
}
