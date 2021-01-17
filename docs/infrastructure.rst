Infrastructure
==============

**Gladier** builds on a science services framework, in the form of Globus Auth, Transfer, Search, Groups, and Flows, plus funcX function-as-a-service. 
These services provide a reliable, secure, and high-performance substrate to access and manage data and computing resources. Here we highlight
several of these services and describe how they are used to create Gladier deployments.

Globus
------

**Globus**  provides a collection of data services built for science 
including: Globus Auth, Transfer, Search, Groups, and Flows, and funcX to enable
distributed function-as-a-service execution. 
Globus Services are highly reliable, professionally operated cloud-hosted 
services that support the work of over 150,000 researchers worldwide as 
foundational capabilities for scientific applications and workflows; 
using them greatly reduces the burden on local systems, administrators, 
and programmers.

Globus Flows
------------
**Flows** addresses
the problem of
securely and reliably automating sequences of data
management tasks that may span
locations, storage systems, administrative domains,
and timescales, and integrate both
mechanical and human inputs.
Client libraries deployed on Globus endpoints and other sources enable the
detection
of events and invocation of a flow.
The Flows service manages execution
of user-supplied
automation flows either manually or as a result
of data events, and the invocation of
actions from those automation flows, including actions
provided by Globus endpoints
and services. The service is extensible via the definition of new events and
actions to
meet the needs of specific communities.


FuncX
-----
**funcX** is a function-as-a-service platform that 
implements a federated compute substrate, 
enabling computation to be 
registered as Python functions and invocations to be dispatched to remote 
computers for
execution. The service provides a single point-of-contact, 
supporting function registration, 
sharing, and discovery as well as reliable and secure execution on connected 
endpoints. The funcX endpoint software, built on Parsl, 
allows functions to 
be executed in containers and for resources to be dynamically provisioned on cloud and 
cluster systems. 
These funcX endpoints provide
serverless capabilities whereby researchers fire-and-forget tasks that are dynamically 
allocated across the supercomputer using an opportunistic backfill queue to utilize 
spare capacity.


Globus Queues and Triggers
--------------------------
**Queues** provides a reliable, cloud-based mechanism to manage and store events.
The Queues service allows users to provision a dedicated queue for their instrument.
Clients can then raise events to the queue using HTTP POST requests where they will be
maintained until a subscriber consumes them. This enables experimental facilities and instruments
to raise events as data are created without requiring heavy-weight installations on the edge device.

The **Triggers** service provides a cloud-based consumer of Queues events. Users can configure a Trigger to monitor a queue and initiate Flows as events are received.
To create a trigger one defines:

- An event queue for the trigger to monitor
- A condition for when the trigger will fire
- An action to perform when the condition is met (e.g., a flow uuid)
- A template to create an input JSON document for the action. This often includes default values.

The combination of the **Queues** and **Triggers** services simplifies creating new Gladier deployments.


Globus Transfer
---------------
**Transfer**  implements a location-agnostic data
substrate that enables data to be
accessed, shared, and moved among disparate storage
systems, including at instruments,
supercomputers, and on data services. Globus Transfer allows
users and applications to modify data access permissions
on remote storage systems and
to move data reliably and securely between systems via a single API.


Globus Auth
-----------
**Auth** Auth allows for users to delegate permissions for clients to access services in the Gladier
architecture, and for services to access other services on their behalf as well.
For example, it allows Globus Flows to manage Globus Transfers and to execute
analyses via funcX on systems accessible only to the user.

